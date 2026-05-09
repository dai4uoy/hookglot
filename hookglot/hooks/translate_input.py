#!/usr/bin/env python3
"""UserPromptSubmit hook — translate user's prompt before Claude sees it.

Used by Method 1 (two-way) and Method 2 (input-only).
Reads a JSON event from stdin, outputs additionalContext as JSON.
"""
import json
import sys
from datetime import datetime

from hookglot.config import load_config, get_provider_config, load_env, CONFIG_DIR
from hookglot.translators.factory import get_translator
from hookglot.translators.base import TranslationError
from hookglot.language import has_target_language_chars, get_language


DEBUG_LOG = CONFIG_DIR / "hook_debug.log"


def debug_log(msg: str):
    """Append timestamped message to debug log."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] [input] {msg}\n")
    except OSError:
        pass


def main():
    # Force UTF-8 stdout/stderr for emoji/non-ASCII safety on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    debug_log("=== hook invoked ===")

    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        debug_log("malformed stdin JSON, exiting")
        sys.exit(0)

    prompt = input_data.get("prompt", "")
    if not prompt.strip():
        debug_log("empty prompt, exiting")
        sys.exit(0)

    # Critical: load API keys from ~/.hookglot/.env
    load_env()

    config = load_config()
    method = config.get("method", 1)

    # Method 2 (output-only) doesn't use input translation
    if method != 1:
        sys.exit(0)

    target_lang_code = config.get("language", "th")

    # Skip if prompt doesn't contain target language characters
    if not has_target_language_chars(prompt, target_lang_code):
        sys.exit(0)

    # Initialize translator
    provider_name = config.get("translator", "ollama")
    try:
        provider_config = get_provider_config(provider_name)
        translator = get_translator(provider_name, provider_config)
    except (ValueError, KeyError) as e:
        print(f"[hookglot] Config error: {e}", file=sys.stderr)
        sys.exit(0)

    # Translate target language → English
    try:
        translated = translator.translate(
            text=prompt,
            source_lang_code=target_lang_code,
            target_lang_code="en",  # always translate to English internally
        )
    except TranslationError as e:
        # Notify user but don't block
        print(
            f"\n⚠️  hookglot: Translation failed via {e.provider} ({e.reason})\n"
            f"   {e.message}\n"
            f"   Prompt sent without translation.\n",
            file=sys.stderr,
        )
        sys.exit(0)

    # Skip if no actual change
    if translated.strip() == prompt.strip():
        debug_log("no translation change, exiting")
        sys.exit(0)

    # Method 1 (input-only): Claude responds in target language directly
    target_lang = get_language(target_lang_code)
    context = (
        f"[English translation of user's {target_lang.english_name} prompt — "
        f"use this for understanding]\n"
        f"\n{translated}\n\n"
        f"INSTRUCTIONS:\n"
        f"- Respond in {target_lang.english_name} ({target_lang.native_name}) "
        f"with natural, fluent sentence structure.\n"
        f"- Keep all technical terms in English.\n"
        f"- Use code blocks for commands and output.\n"
    )

    debug_log(f"injecting EN context, {len(translated)} chars")

    # Output as additionalContext per Claude Code hook spec
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
