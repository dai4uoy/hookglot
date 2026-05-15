#!/usr/bin/env python3
"""Stop hook — translate Claude's response (Method 2) and log conversations (Methods 1 & 2).

Behavior:
- Method 1 (input-only): Claude responds in target language directly.
  Stop hook walks transcript and logs user+claude to conversation.md.
  No translation happens. No "Stop says:" output.
- Method 2 (output-only): Claude responds in English.
  Stop hook walks transcript, collects ALL assistant blocks from current turn,
  translates the combined text, logs translated version to conversation.md,
  prints translation to stderr for Claude Code UI.

Walk-back strategy:
  Read transcript from bottom up, collecting assistant text blocks until we hit
  a real user message (not a tool_result). Safety guards prevent runaway reads.
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

from hookglot.config import load_config, get_provider_config, load_env, CONFIG_DIR
from hookglot.translators.factory import get_translator
from hookglot.translators.base import TranslationError
from hookglot.language import get_language, has_target_language_chars


CONVERSATION_FILE = CONFIG_DIR / "conversation.md"
DEBUG_LOG = CONFIG_DIR / "hook_debug.log"

# Safety guards — prevent runaway transcript reads and oversized translations
MAX_LOOKBACK_LINES = 100        # Don't walk back more than this many lines
MAX_BLOCKS_TO_COLLECT = 10      # Cap on assistant blocks per turn
MAX_CHARS_TO_TRANSLATE = 20000  # Cap on text sent to translator


def debug_log(msg: str):
    """Append timestamped message to debug log."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] [stop] {msg}\n")
    except OSError:
        pass


def append_conversation(user_msg: str, claude_msg: str):
    """Append a turn to ~/.hookglot/conversation.md."""
    if not user_msg and not claude_msg:
        return
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        is_new = not CONVERSATION_FILE.exists()
        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
            if is_new:
                f.write("# Conversation Log\n\n")
            if user_msg:
                f.write(f"User: {user_msg.strip()}\n\n")
            if claude_msg:
                f.write(f"Claude: {claude_msg.strip()}\n\n")
            f.write("---\n\n")
    except OSError as e:
        debug_log(f"Failed to write conversation: {e}")


def is_real_user_message(content) -> bool:
    """A real user message is a string, or a list of blocks where none are tool_result."""
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        if not content:
            return False
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                return False
        return True
    return False


def extract_text_from_content(content) -> str:
    """Extract plain text from content. Skips tool_use, tool_result, etc."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                t = block.get("text", "")
                if t:
                    texts.append(t)
        return "\n".join(texts)
    return ""


def walk_back_transcript(transcript_path: str):
    """Walk back through transcript collecting assistant blocks until user message.

    Returns:
        (user_message_text, [block1, block2, ...]) — assistant blocks in original order.
        Either may be None/empty if not found.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return None, []

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        debug_log(f"transcript read error: {e}")
        return None, []

    # Limit lookback window
    if len(lines) > MAX_LOOKBACK_LINES:
        lines = lines[-MAX_LOOKBACK_LINES:]

    assistant_blocks = []
    user_message = None

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue  # skip malformed (concurrent write etc.)

        # Schema can vary — check both 'role' and 'type'
        role = entry.get("role") or entry.get("type") or ""
        msg = entry.get("message", entry)
        if not isinstance(msg, dict):
            continue
        content = msg.get("content", "")

        if role == "user":
            if is_real_user_message(content):
                user_message = extract_text_from_content(content)
                break  # found boundary — stop
            # else: tool_result, keep walking back
        elif role == "assistant":
            text = extract_text_from_content(content)
            if text:
                assistant_blocks.append(text)
                if len(assistant_blocks) >= MAX_BLOCKS_TO_COLLECT:
                    break

    assistant_blocks.reverse()  # back to original order
    debug_log(
        f"walked back: user_msg={'yes' if user_message else 'no'}, "
        f"blocks={len(assistant_blocks)}"
    )
    return user_message, assistant_blocks


def main():
    # Force UTF-8 stdout/stderr for emoji/non-ASCII safety on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    debug_log("=== hook invoked ===")

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        debug_log("malformed stdin JSON, exiting")
        sys.exit(0)

    # Load API keys from ~/.hookglot/.env
    load_env()

    config = load_config()
    method = config.get("method", 1)
    debug_log(
        f"method={method}, translator={config.get('translator')}, "
        f"lang={config.get('language')}"
    )

    # Only Method 1 and 2 use Stop hook
    if method not in (1, 2):
        debug_log(f"method {method} doesn't use Stop hook")
        sys.exit(0)

    transcript_path = input_data.get("transcript_path", "")
    user_msg, assistant_blocks = walk_back_transcript(transcript_path)

    if not assistant_blocks:
        debug_log("no assistant blocks collected, exiting")
        sys.exit(0)

    # Combine all blocks from current turn into one response
    full_response = "\n\n".join(assistant_blocks)

    # Bypass marker — slash commands and internal outputs skip translation/logging
    BYPASS_MARKERS = ["[hg-bypass]", "<!--hg-bypass-->", "<!-- hg-bypass -->"]
    head = full_response[:300]
    for marker in BYPASS_MARKERS:
        if marker in head:
            debug_log(f"bypass marker '{marker}' found, skipping")
            sys.exit(0)

    target_lang_code = config.get("language", "th")
    target_lang = get_language(target_lang_code)

    # ─────────────────────────────────────────────────
    # Method 1: Claude responded in target language directly
    # No translation needed — just log to conversation.md
    # ─────────────────────────────────────────────────
    if method == 1:
        append_conversation(user_msg, full_response)
        debug_log(f"method 1: logged {len(full_response)} chars to conversation.md")
        sys.exit(0)

    # ─────────────────────────────────────────────────
    # Method 2: translate then log + display
    # ─────────────────────────────────────────────────

    # Defensive: if response already mostly in target language, skip translation
    if has_target_language_chars(full_response, target_lang_code):
        if not target_lang.uses_latin:
            target_count = sum(
                1 for c in full_response
                for start, end in target_lang.unicode_ranges
                if start <= ord(c) <= end
            )
            if target_count > len(full_response) * 0.3:
                debug_log("response already mostly in target lang, skipping translation")
                append_conversation(user_msg, full_response)
                sys.exit(0)

    # Cap translation size — fallback to last block only if too big
    if len(full_response) > MAX_CHARS_TO_TRANSLATE:
        debug_log(
            f"response too long ({len(full_response)} chars), "
            f"falling back to last block only"
        )
        full_response = assistant_blocks[-1] if assistant_blocks else ""
        if not full_response:
            sys.exit(0)

    # Initialize translator
    provider_name = config.get("translator", "ollama")
    try:
        provider_config = get_provider_config(provider_name)
        translator = get_translator(provider_name, provider_config)
    except (ValueError, KeyError) as e:
        print(f"\n[hookglot] Config error: {e}", file=sys.stderr)
        sys.exit(1)

    # Translate English → target language
    try:
        translated = translator.translate(
            text=full_response,
            source_lang_code="en",
            target_lang_code=target_lang_code,
        )
    except TranslationError as e:
        sep = "─" * 60
        print(
            f"\n{sep}\n"
            f"⚠️  Translation failed\n"
            f"{sep}\n"
            f"Provider : {e.provider}\n"
            f"Reason   : {e.reason}\n"
            f"Message  : {e.message}\n"
            f"Action   : Output shown in English only\n"
            f"\n"
            f"To switch translator:\n"
            f"  hookglot translator <provider>\n"
            f"\n"
            f"To check status:\n"
            f"  hookglot status\n"
            f"{sep}\n",
            file=sys.stderr,
        )
        sys.exit(1)

    # Log Thai version to conversation.md
    append_conversation(user_msg, translated)
    debug_log(
        f"method 2: translated {len(full_response)} chars → {len(translated)} chars, logged"
    )

    # Display translation in Claude Code UI via stderr
    print(f"\n\n{translated}\n", file=sys.stderr)

    # Also emit JSON for Windows Claude Code (stderr UI may differ)
    try:
        sys.stdout.write(json.dumps({
            "suppressOutput": False,
            "systemMessage": f"\n\n{translated}\n",
        }))
    except Exception:
        pass


if __name__ == "__main__":
    main()
