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

TODO (future refactor):
  This module currently mixes two responsibilities:
    1. Translation (Method 2 only)
    2. Conversation logging (Methods 1 & 2)
  Consider splitting into:
    - hookglot/hooks/translate_output.py  (translation only)
    - hookglot/hooks/log_conversation.py  (logging only)
    - hookglot/hooks/_transcript.py       (shared walk_back helper)
  Trigger for refactor: when adding a 3rd logging-related feature (summary,
  analytics, export, etc.) or when this file grows beyond ~400 LOC.
  Tradeoff: split adds ~200ms latency in Method 2 (extra subprocess spawn
  + duplicate transcript read), but improves testability and future-proofing.
"""
import json
import re
import sys
import os
from pathlib import Path
from datetime import datetime

from hookglot.config import load_config, get_provider_config, load_env, CONFIG_DIR
from hookglot.translators.factory import get_translator
from hookglot.translators.base import TranslationError
from hookglot.language import get_language, has_target_language_chars


CONVERSATIONS_DIR = CONFIG_DIR / "conversations"
SESSIONS_MAP = CONFIG_DIR / "sessions.json"
LEGACY_CONVERSATION = CONFIG_DIR / "conversation.md"
DEBUG_LOG = CONFIG_DIR / "hook_debug.log"

# Hidden signature (two zero-width spaces) prepended to translated stderr output.
# Used to identify hookglot's OWN Stop-hook leak in the transcript so cleanup
# never touches other plugins' hook_success entries (e.g. caveman).
HOOKGLOT_SIG = "\u200b\u200b"


# Lazy cleanup: only rewrite the transcript once this many leaked entries have
# accumulated, instead of every turn. Batching keeps per-turn latency near zero
# (most turns just read + count; the write happens once per N turns).
LAZY_CLEANUP_THRESHOLD = 5


def cleanup_previous_leak(transcript_path: str):
    """Remove hookglot's own leaked display output from the transcript (lazy).

    Background: when inline display is on, Claude Code captures the Stop hook's
    systemMessage into the transcript as a `hook_system_message` attachment.
    Testing showed this does NOT reach Anthropic billing (the harness filters
    Stop-hook stdout out of context), so cleanup is purely a disk-hygiene /
    future-proofing measure — hence "lazy".

    Lazy strategy: each turn we read the transcript and count leaked entries
    carrying HOOKGLOT_SIG. We only rewrite the file once at least
    LAZY_CLEANUP_THRESHOLD have piled up. This makes most turns a cheap
    read-and-count with no write.

    Only `hook_system_message` entries carrying HOOKGLOT_SIG are removed, so
    stderr error notices and other plugins' hooks are never touched.

    Atomic write (temp + os.replace) guarantees the transcript is never left
    half-written even if the process is killed mid-cleanup. Lock/permission
    failures are swallowed — the batch is simply cleaned on a later turn.
    """
    if not transcript_path:
        return
    tpath = Path(transcript_path)
    if not tpath.exists():
        return

    try:
        with open(tpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (IOError, OSError, PermissionError):
        return  # locked / unavailable — retry next turn

    def is_leak(line: str) -> bool:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return False
        if entry.get("type") != "attachment":
            return False
        att = entry.get("attachment", {})
        if not isinstance(att, dict):
            return False
        if att.get("hookName") != "Stop":
            return False
        if att.get("type") != "hook_system_message":
            return False
        body = (att.get("content", "") or att.get("stdout", "") or "")
        return HOOKGLOT_SIG in body

    leak_count = sum(1 for ln in lines if is_leak(ln))

    # Lazy gate: wait until enough leaks accumulate before paying for a rewrite.
    if leak_count < LAZY_CLEANUP_THRESHOLD:
        return

    kept = [ln for ln in lines if not is_leak(ln)]

    # Atomic write: temp file in same dir, then os.replace
    tmp = tpath.with_suffix(tpath.suffix + ".hgtmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.writelines(kept)
        os.replace(tmp, tpath)  # atomic on all OSes
        debug_log(f"cleanup: removed {leak_count} leaked entry(ies) (lazy batch)")
    except (IOError, OSError, PermissionError) as e:
        debug_log(f"cleanup: write failed ({e}) — will retry next turn")
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass

# Safety guards — prevent runaway transcript reads and oversized translations
MAX_LOOKBACK_LINES = 100        # Don't walk back more than this many lines
MAX_BLOCKS_TO_COLLECT = 10      # Cap on assistant blocks per turn
MAX_CHARS_TO_TRANSLATE = 12000  # Cap on text sent to translator (was 20k in v1.3 —
                                # reduced in v1.4 to cap DeepSeek cost on long responses)


def debug_log(msg: str):
    """Append timestamped message to debug log."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] [stop] {msg}\n")
    except OSError:
        pass


def _sanitize_title(s: str, maxlen: int = 50) -> str:
    """Make a string safe for a filename: lowercase, hyphen-separated, no junk."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)      # drop punctuation/symbols
    s = re.sub(r"[\s_]+", "-", s)        # whitespace/underscore → hyphen
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:maxlen].strip("-") or "session"


def generate_session_title(text: str, translator=None) -> str:
    """Make a short filename title for a session.

    If a translator is available, ask it for a 3–6 word English title (one extra
    provider call — happens ONCE per session, only when the file is first created).
    On any failure, or when no translator is given, fall back to the first few
    words of the text (free, no API call).
    """
    text = (text or "").strip()
    if not text:
        return "session"
    if translator is not None:
        try:
            prompt = (
                "Create a concise English title (3 to 6 words) summarizing the "
                "user's request, suitable for a filename. Output ONLY the title "
                "text — no quotes, no punctuation, no explanation."
            )
            raw = translator._call_api(prompt, text[:500])
            t = _sanitize_title(raw)
            if t and t != "session":
                return t
        except Exception as e:
            debug_log(f"title gen failed, using fallback: {e}")
    # Fallback: first ~6 words of the text
    words = re.sub(r"[^\w\s-]", "", text).split()[:6]
    return _sanitize_title(" ".join(words))


def _new_session_title(session_id: str, user_msg: str, translator=None) -> str:
    """Title for a session's file — generated ONLY when the session is new.

    Returns "" for an already-seen session so no extra provider call is made on
    later turns. The AI title (1 provider call) thus happens once per session.
    """
    mapping = _load_sessions_map()
    if session_id and session_id in mapping:
        existing = CONVERSATIONS_DIR / mapping[session_id]
        if existing.exists():
            return ""
    return generate_session_title(user_msg, translator)


def get_session_id_from_transcript(transcript_path: str) -> str:
    """Extract session ID from transcript path.

    Transcript paths look like:
      <claude_dir>/projects/<encoded-project>/<session-id>.jsonl
    """
    if not transcript_path:
        return ""
    try:
        return Path(transcript_path).stem
    except Exception:
        return ""


def _load_sessions_map() -> dict:
    """Load session_id → filename mapping."""
    if not SESSIONS_MAP.exists():
        return {}
    try:
        with open(SESSIONS_MAP, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_sessions_map(mapping: dict):
    """Persist session_id → filename mapping."""
    try:
        with open(SESSIONS_MAP, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2)
    except OSError as e:
        debug_log(f"Failed to write sessions map: {e}")


def _get_or_create_session_file(session_id: str, title: str = "") -> Path:
    """Return the conversation file path for this session.

    Layout: ~/.hookglot/conversations/<dd.mm.yy>/<ai-title>.md
    Creates the dated folder + AI-titled file on first encounter, then reuses it
    for subsequent turns (looked up via sessions.json).
    """
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

    mapping = _load_sessions_map()

    # Existing session — reuse file if still present
    if session_id and session_id in mapping:
        existing = CONVERSATIONS_DIR / mapping[session_id]
        if existing.exists():
            return existing

    # New session — create <dd.mm.yy>/<title>.md
    date_folder = datetime.now().strftime("%d.%m.%y")
    folder = CONVERSATIONS_DIR / date_folder
    folder.mkdir(parents=True, exist_ok=True)

    base = _sanitize_title(title) if title else datetime.now().strftime("%H-%M-%S")
    filename = f"{base}.md"
    rel = f"{date_folder}/{filename}"

    # Handle collision (same title same day)
    counter = 1
    while (CONVERSATIONS_DIR / rel).exists():
        filename = f"{base}-{counter}.md"
        rel = f"{date_folder}/{filename}"
        counter += 1

    filepath = CONVERSATIONS_DIR / rel
    if session_id:
        mapping[session_id] = rel
        _save_sessions_map(mapping)

    # Write header
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            if session_id:
                f.write(f"# claude --resume {session_id}\n\n")
    except OSError as e:
        debug_log(f"Failed to create session file: {e}")

    return filepath


def _write_turn(filepath: Path, user_msg: str, claude_msg: str):
    """Append a single turn (user + claude) to a file in heading format."""
    with open(filepath, "a", encoding="utf-8") as f:
        if user_msg:
            f.write(f"## 🖥️ User\n\n{user_msg.strip()}\n\n")
        if claude_msg:
            f.write(f"## 🤖 Claude\n\n{claude_msg.strip()}\n\n")
        # Minimal centered divider between turns
        f.write('<div align="center">⸻ ✦ ⸻</div>\n\n')


def append_conversation(user_msg: str, claude_msg: str, session_id: str = "", title: str = ""):
    """Append a turn to BOTH:
    - Per-session file (~/.hookglot/conversations/<dd.mm.yy>/<ai-title>.md)
    - Cumulative file (~/.hookglot/conversation.md) — clearable via /hookglot-clear-chat

    `title` is only used when the per-session file is first created.
    """
    if not user_msg and not claude_msg:
        return

    # 1. Per-session file (manual delete only)
    try:
        session_file = _get_or_create_session_file(session_id, title)
        _write_turn(session_file, user_msg, claude_msg)
    except OSError as e:
        debug_log(f"Failed to write session file: {e}")

    # 2. Cumulative conversation.md (cleared by /hookglot-clear-chat)
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        _write_turn(LEGACY_CONVERSATION, user_msg, claude_msg)
    except OSError as e:
        debug_log(f"Failed to write conversation.md: {e}")


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

    # Lazy cleanup of leaked display entries — only relevant when inline display
    # is on (that's the only thing that writes leaks). Skipped entirely when
    # display is off, so the default config pays zero cleanup overhead.
    if config.get("output", False):
        cleanup_previous_leak(transcript_path)

    user_msg, assistant_blocks = walk_back_transcript(transcript_path)
    session_id = get_session_id_from_transcript(transcript_path)
    debug_log(f"session_id={session_id or '(none)'}")

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
    # No translation needed — just log to conversation file
    # ─────────────────────────────────────────────────
    if method == 1:
        title = _new_session_title(session_id, user_msg)
        append_conversation(user_msg, full_response, session_id, title)
        debug_log(f"method 1: logged {len(full_response)} chars (session={session_id[:8] if session_id else 'unknown'})")
        sys.exit(0)

    # ─────────────────────────────────────────────────
    # Method 2: translate then log + display
    # ─────────────────────────────────────────────────

    # Defensive: if response is already mostly in target language, skip translation.
    # This catches the case where Claude ignores Master Prompt and responds in target
    # language anyway (would otherwise cause "language flip" bug: TH→EN translation).
    # Strip code blocks and inline code first, since those are naturally English
    # and would dilute the Thai ratio below threshold.
    if has_target_language_chars(full_response, target_lang_code):
        if not target_lang.uses_latin:
            # Strip code blocks (```...```) and inline code (`...`)
            cleaned = re.sub(r'```[\s\S]*?```', '', full_response)
            cleaned = re.sub(r'`[^`\n]+`', '', cleaned)
            cleaned_len = max(len(cleaned), 1)  # avoid divide-by-zero
            target_count = sum(
                1 for c in cleaned
                for start, end in target_lang.unicode_ranges
                if start <= ord(c) <= end
            )
            ratio = target_count / cleaned_len
            debug_log(f"target_lang ratio (after stripping code): {ratio:.2f}")
            if ratio > 0.25:
                debug_log("response already mostly in target lang, skipping translation")
                title = _new_session_title(session_id, user_msg)
                append_conversation(user_msg, full_response, session_id, title)
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

    # Log Thai version to conversation file (AI title on first turn of session)
    title = _new_session_title(session_id, user_msg, translator)
    append_conversation(user_msg, translated, session_id, title)
    debug_log(
        f"method 2: translated {len(full_response)} chars → {len(translated)} chars, logged"
    )

    # Optional inline display ("Stop says: …"). OFF by default; toggled with
    # `hookglot switch --output`. When on, the translation is emitted as a
    # systemMessage (stdout JSON) — the only channel Claude Code actually renders
    # for Stop hooks (exit-0 stderr is never shown per the hook spec, and was
    # confirmed not to display on Windows/macOS/Linux in testing).
    #
    # The hidden signature (HOOKGLOT_SIG) lets the lazy cleanup identify and
    # remove these entries from the transcript later. (Testing showed they don't
    # reach Anthropic billing regardless — the harness filters Stop-hook stdout —
    # so cleanup is disk-hygiene only.)
    #
    # stderr is intentionally NOT used for display (it never renders); it is
    # reserved for error notices above.
    if config.get("output", False):
        try:
            sys.stdout.write(json.dumps({
                "suppressOutput": False,
                "systemMessage": f"\n\n{HOOKGLOT_SIG}{translated}\n",
            }))
        except Exception:
            pass


if __name__ == "__main__":
    main()
