#!/usr/bin/env python3
"""Stop hook — translate Claude's English response to user's local language.

Used by Method 1 (two-way) and Method 3 (output-only).
Reads transcript, finds last assistant message, translates, prints to stderr.

Note: Claude Code already streamed the English to the user. This hook appends
the translation as additional info — it does NOT replace the streamed output.
On Windows, Claude Code may not display stderr in the UI; we also write the
last translation to ~/.hookglot/last_translation.txt as a fallback.
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


LAST_TRANSLATION_FILE = CONFIG_DIR / "last_translation.txt"
DEBUG_LOG = CONFIG_DIR / "hook_debug.log"


def debug_log(msg: str):
    """Append timestamped message to debug log."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] [stop] {msg}\n")
    except OSError:
        pass


def write_last_translation(translation: str, lang_code: str):
    """Write translation to fallback file (always works, regardless of UI)."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LAST_TRANSLATION_FILE, "w", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"# Last translation ({lang_code}) — {ts}\n\n")
            f.write(translation)
    except OSError as e:
        debug_log(f"Failed to write last_translation: {e}")


def read_last_assistant_message(transcript_path: str):
    """Parse JSONL transcript and return last assistant message text."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Match assistant entries (format may vary across Claude Code versions)
        if entry.get("type") == "assistant" or entry.get("role") == "assistant":
            msg = entry.get("message", entry)
            content = msg.get("content", "")

            if isinstance(content, str):
                return content
            if isinstance(content, list):
                texts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text", ""))
                if texts:
                    return "\n".join(texts)
    return None


def main():
    # Force UTF-8 stdout/stderr for emoji/non-ASCII safety on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    # Log entry immediately — proves hook was invoked, even if everything else fails
    debug_log("=== hook invoked ===")

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        debug_log("malformed stdin JSON, exiting")
        sys.exit(0)

    # Critical: load API keys from ~/.hookglot/.env into os.environ
    # Hooks spawned as subprocesses may not inherit shell env vars
    load_env()

    config = load_config()
    method = config.get("method", 1)
    debug_log(f"method={method}, translator={config.get('translator')}, lang={config.get('language')}")

    # Output translation only used by Method 2
    if method != 2:
        debug_log(f"method {method} doesn't use output translation — skipping")
        sys.exit(0)

    transcript_path = input_data.get("transcript_path", "")
    response = read_last_assistant_message(transcript_path)
    if not response or not response.strip():
        sys.exit(0)

    # Bypass marker — slash commands and other internal outputs include this
    # so the Stop hook doesn't translate them (avoids double-display).
    BYPASS_MARKERS = ["[hg-bypass]", "<!--hg-bypass-->", "<!-- hg-bypass -->"]
    head = response[:300]
    for marker in BYPASS_MARKERS:
        if marker in head:
            debug_log(f"bypass marker '{marker}' found, skipping translation")
            sys.exit(0)

    target_lang_code = config.get("language", "th")

    # Defensive: if response is already in target language (>50% chars), skip
    if has_target_language_chars(response, target_lang_code):
        # Quick heuristic: count target language chars
        target_lang = get_language(target_lang_code)
        if not target_lang.uses_latin:
            target_count = sum(
                1 for c in response
                for start, end in target_lang.unicode_ranges
                if start <= ord(c) <= end
            )
            if target_count > len(response) * 0.3:
                # Already mostly in target language — likely Method 2 ran
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
            text=response,
            source_lang_code="en",
            target_lang_code=target_lang_code,
        )
    except TranslationError as e:
        # Notify user clearly that translation failed
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

    # Display translated version
    target_lang = get_language(target_lang_code)

    # Write to fallback file FIRST (always works, regardless of UI)
    write_last_translation(translated, target_lang_code)
    debug_log(f"translated {len(response)} chars → {len(translated)} chars (saved to file)")

    # Clean output — no separator, no header, no flag.
    # Claude Code already shows "Stop says:" prefix; the content blends
    # into Claude's native response style.
    # Print to stderr with leading blank line so Claude Code's "Stop says:"
    # block is visually separated from Claude's main response.
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
