"""hookglot CLI commands.

Commands:
    install              Interactive setup
    status               Show current configuration
    switch <method>      Switch method (1, 2, 3)
    translator <name>    Switch translator provider
    lang <code>          Switch target language
    set-key <provider>   Set API key for a provider
    test                 Test translation works
    uninstall            Remove hooks from Claude Code
"""
import argparse
import sys
import json
import os
from pathlib import Path

from hookglot import __version__
from hookglot.config import (
    load_config, save_config, write_env_file, load_env,
    get_provider_config, CONFIG_DIR, CONFIG_FILE, DEFAULT_CONFIG,
)
from hookglot.language import LANGUAGES, get_language
from hookglot.translators.factory import get_translator, SUPPORTED_PROVIDERS


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def colored(text: str, color: str) -> str:
    """Add ANSI color (no-op if not a TTY)."""
    if not sys.stdout.isatty():
        return text
    colors = {
        "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
        "blue": "\033[34m", "cyan": "\033[36m", "bold": "\033[1m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def prompt_choice(message: str, options: list, default: int = 1) -> int:
    """Prompt user for a numeric choice."""
    print(f"\n{colored(message, 'bold')}")
    for i, opt in enumerate(options, 1):
        marker = " ⭐" if i == default else ""
        print(f"  {i}) {opt}{marker}")
    while True:
        choice = input(f"\nChoice [{default}]: ").strip()
        if not choice:
            return default
        try:
            n = int(choice)
            if 1 <= n <= len(options):
                return n
        except ValueError:
            pass
        print(colored("Invalid choice, try again.", "red"))


def get_claude_settings_path() -> Path:
    """Get path to Claude Code settings.json."""
    return Path.home() / ".claude" / "settings.json"


def get_claude_md_path() -> Path:
    """Get path to ~/.claude/CLAUDE.md."""
    return Path.home() / ".claude" / "CLAUDE.md"


def get_repo_root() -> Path:
    """Find repo root (where prompts/ and settings/ live)."""
    # When installed via pip, files live alongside hookglot package
    pkg_dir = Path(__file__).parent.parent.parent
    if (pkg_dir / "prompts").exists():
        return pkg_dir
    # Fallback: search
    return Path(__file__).parent.parent


# ─────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────
def find_project_claude_settings():
    """Walk up from cwd looking for a project-level .claude/settings.json.

    Returns the path if found, None otherwise. Stops before reaching $HOME
    so the global ~/.claude/settings.json isn't mistakenly returned.
    """
    home = Path.home().resolve()
    current = Path.cwd().resolve()

    while True:
        if current == home:
            return None
        candidate = current / ".claude" / "settings.json"
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def project_has_hookglot_hooks(settings_path):
    """Check if a settings.json file already contains hookglot hook entries."""
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False

    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        return False

    for matchers in hooks.values():
        if not isinstance(matchers, list):
            continue
        for matcher in matchers:
            if not isinstance(matcher, dict):
                continue
            for h in matcher.get("hooks", []):
                if is_hookglot_command(h.get("command", "")):
                    return True
    return False


def warn_about_project_claude(method):
    """Detect project-level .claude/settings.json. Show snippet only if hookglot
    hooks aren't already there.
    """
    project_settings = find_project_claude_settings()
    if not project_settings:
        return

    if project_has_hookglot_hooks(project_settings):
        return  # Already configured in project — no warn needed

    python_cmd = get_python_command()
    if method == 1:
        event = "UserPromptSubmit"
        cmd = f"{python_cmd} -m hookglot.hooks.translate_input"
        timeout = 60
    else:
        event = "Stop"
        cmd = f"{python_cmd} -m hookglot.hooks.translate_output"
        timeout = 90

    print(colored(f"\n⚠️  Project-level settings detected:", "yellow"))
    print(f"     {project_settings}")
    print(colored(
        "\n   Claude Code uses project settings instead of global when running here.",
        "yellow",
    ))
    print(colored(
        "   If hookglot doesn't work in this project, add this to that file's"
        f' "hooks" → "{event}" array:\n',
        "yellow",
    ))

    snippet = {
        "hooks": {
            event: [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": cmd,
                            "timeout": timeout,
                        }
                    ]
                }
            ]
        }
    }
    for line in json.dumps(snippet, indent=2).splitlines():
        print(colored(f"     {line}", "cyan"))
    print()


def cmd_install(args):
    """Interactive installation."""
    print(colored("\n🌐 hookglot installer", "bold"))
    print(f"Version {__version__}\n")

    # Check Claude Code
    settings_path = get_claude_settings_path()
    if not settings_path.parent.exists():
        print(colored("⚠️  ~/.claude not found. Is Claude Code installed?", "yellow"))
        cont = input("Continue anyway? [y/N]: ").strip().lower()
        if cont != "y":
            sys.exit(1)

    # Step 1: Language
    lang_codes = list(LANGUAGES.keys())
    lang_options = [f"{LANGUAGES[c].english_name} ({LANGUAGES[c].native_name})" for c in lang_codes]
    lang_idx = prompt_choice("[1/5] Choose your language:", lang_options, default=1)
    language = lang_codes[lang_idx - 1]

    # Step 2: Method
    method_options = [
        "Input-only (Claude responds in your language directly — recommended)",
        "Output-only (Claude responds in English, then translated below)",
    ]
    method = prompt_choice("[2/5] Choose translation method:", method_options, default=1)

    # Step 3: Translator
    translator_options = [
        "Ollama (free, local, no API key needed)",
        "OpenAI (gpt-4o-mini)",
        "Anthropic (claude-haiku-4-5)",
        "Google Gemini (free tier available)",
        "DeepSeek (cheapest cloud, great for Asian languages)",
        "Alibaba Qwen (DashScope)",
        "Moonshot",
        "Zhipu AI (free tier available)",
        "NVIDIA (Llama via NVIDIA)",
    ]
    provider_idx = prompt_choice("[3/5] Choose translator provider:", translator_options, default=1)
    translator = SUPPORTED_PROVIDERS[provider_idx - 1]

    # Step 4: API key (if cloud provider)
    if translator != "ollama":
        provider_cfg = get_provider_config(translator)
        env_var = provider_cfg.get("api_key_env", "")
        print(f"\n{colored(f'[4/5] {translator.title()} requires API key', 'bold')}")
        print(f"Env variable: {env_var}")
        existing = os.environ.get(env_var, "")
        if existing:
            print(colored(f"Found existing key in environment ({len(existing)} chars)", "green"))
            use_existing = input("Use existing? [Y/n]: ").strip().lower()
            if use_existing != "n":
                api_key = existing
            else:
                api_key = input(f"Enter {env_var}: ").strip()
        else:
            api_key = input(f"Enter {env_var}: ").strip()

        if api_key:
            write_env_file({env_var: api_key})
            print(colored(f"✅ Key saved to ~/.hookglot/.env", "green"))

    # Step 5: Optional model override
    default_model = DEFAULT_CONFIG["providers"][translator]["model"]
    print(f"\n{colored('[5/5] Model selection (optional)', 'bold')}")
    print(f"Default model for {translator}: {colored(default_model, 'cyan')}")
    print("Press Enter to use default, or type a custom model name.")
    custom_model = input(f"Model: ").strip()

    # Save config
    config = load_config()
    config["language"] = language
    config["method"] = method
    config["translator"] = translator
    if custom_model:
        config["providers"][translator]["model"] = custom_model
        print(colored(f"✅ Using custom model: {custom_model}", "green"))
    else:
        print(colored(f"✅ Using default model: {default_model}", "green"))
    save_config(config)
    print(colored(f"\n✅ Config saved to {CONFIG_FILE}", "green"))

    # Warn about project-level .claude/ that overrides global (smart check)
    warn_about_project_claude(method)

    # Install hooks into Claude Code settings (safe merge)
    install_hooks(method)

    # Install Master Prompt (preserves user content via markers)
    install_master_prompt(language, method)

    # Install slash commands
    install_slash_commands()

    print(colored("\n🎉 Installation complete!", "green"))
    print("\nNext steps:")
    print(f"  1. Test: {colored('hookglot test', 'cyan')}")
    print(f"  2. Status: {colored('hookglot status', 'cyan')}")
    print(f"  3. Use: {colored('claude', 'cyan')}")


def get_python_command() -> str:
    """Get a quoted Python command string for hook configuration.

    Uses sys.executable (full path to current Python) so the hook works
    regardless of OS or whether `python` vs `python3` is available.

    On Windows: Claude Code invokes hooks through bash (Git Bash bundled
    with Claude Code), where backslashes are escape characters. Convert
    to forward slashes — works in both bash and cmd.exe on Windows.
    """
    py = sys.executable
    if sys.platform == "win32":
        # Forward slashes work in bash AND cmd.exe on Windows.
        # Backslashes get eaten by bash as escape chars (e.g., \U, \g).
        py = py.replace("\\", "/")
    # Quote if path contains spaces (common: "C:/Program Files/Python/python.exe")
    if " " in py:
        py = f'"{py}"'
    return py


def is_hookglot_command(cmd_str: str) -> bool:
    """Check if a hook command belongs to hookglot."""
    return "hookglot.hooks." in (cmd_str or "")


def remove_hookglot_hooks_from_settings(settings: dict) -> dict:
    """Remove only hookglot's hook entries from settings, keeping other hooks intact."""
    if "hooks" not in settings:
        return settings

    cleaned_events = {}
    for event_name, matchers in settings["hooks"].items():
        if not isinstance(matchers, list):
            cleaned_events[event_name] = matchers
            continue

        cleaned_matchers = []
        for matcher in matchers:
            if not isinstance(matcher, dict):
                cleaned_matchers.append(matcher)
                continue
            inner_hooks = matcher.get("hooks", [])
            kept = [h for h in inner_hooks if not is_hookglot_command(h.get("command", ""))]
            if kept:
                # Keep matcher with non-hookglot hooks
                new_matcher = {**matcher, "hooks": kept}
                cleaned_matchers.append(new_matcher)
            # else: matcher only had hookglot hooks → drop entirely
        if cleaned_matchers:
            cleaned_events[event_name] = cleaned_matchers
        # else: event had only hookglot hooks → drop event

    if cleaned_events:
        settings["hooks"] = cleaned_events
    else:
        settings.pop("hooks", None)
    return settings


def install_hooks(method: int):
    """Write hookglot hooks into ~/.claude/settings.json (safe merge).

    Strategy: load existing settings, remove any old hookglot hook entries,
    add new ones for the chosen method. Other user hooks (including for the
    same event types) are preserved.
    """
    settings_path = get_claude_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    python_cmd = get_python_command()

    # Load existing settings
    settings = {}
    if settings_path.exists():
        is_corrupt = False
        with open(settings_path, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                is_corrupt = True
        
        if is_corrupt:
            print(colored(f"\n❌ Error: {settings_path} is not valid JSON.", "red"))
            print(colored("Please fix the file manually before running this command.", "yellow"))
            sys.exit(1)
                


    # Remove any previous hookglot entries (preserve other user hooks)
    settings = remove_hookglot_hooks_from_settings(settings)

    # Build our new hook entries
    new_entries = {}
    if method == 1:
        # Method 1 (input-only): Claude responds in target language directly
        new_entries["UserPromptSubmit"] = {
            "hooks": [
                {
                    "type": "command",
                    "command": f"{python_cmd} -m hookglot.hooks.translate_input",
                    "timeout": 60,
                }
            ]
        }
    elif method == 2:
        # Method 2 (output-only): Master Prompt + Stop hook
        new_entries["Stop"] = {
            "hooks": [
                {
                    "type": "command",
                    "command": f"{python_cmd} -m hookglot.hooks.translate_output",
                    "timeout": 90,
                }
            ]
        }

    # Merge into existing hooks structure
    existing_hooks = settings.get("hooks", {})
    for event_name, matcher in new_entries.items():
        existing_matchers = existing_hooks.get(event_name, [])
        existing_matchers.append(matcher)
        existing_hooks[event_name] = existing_matchers
    if existing_hooks:
        settings["hooks"] = existing_hooks

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    print(colored(f"✅ Hooks merged into {settings_path}", "green"))


def install_slash_commands():
    """Install hookglot slash commands into ~/.claude/commands/.

    These let users switch method/translator/lang from inside Claude Code
    via /hookglot-method, /hookglot-translator, /hookglot-lang, etc.
    """
    repo_root = get_repo_root()
    src_dir = repo_root / "prompts" / "slash_commands"

    if not src_dir.exists():
        print(colored(f"⚠️  Slash command templates not found at {src_dir}", "yellow"))
        return

    dest_dir = Path.home() / ".claude" / "commands"
    dest_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    for src_file in src_dir.glob("*.md"):
        dest_file = dest_dir / src_file.name
        try:
            content = src_file.read_text(encoding="utf-8")
            dest_file.write_text(content, encoding="utf-8")
            installed.append(src_file.stem)
        except OSError as e:
            print(colored(f"⚠️  Failed to install {src_file.name}: {e}", "yellow"))

    if installed:
        print(colored(f"✅ Slash commands installed: /{', /'.join(installed)}", "green"))


HOOKGLOT_MARKER_START = "<!-- HOOKGLOT-START — auto-generated, do not edit between markers -->"
HOOKGLOT_MARKER_END = "<!-- HOOKGLOT-END -->"


def install_master_prompt(language: str, method: int):
    """Install Master Prompt into ~/.claude/CLAUDE.md (merge-safe).

    Strategy:
    - If the file doesn't exist → create it with the hookglot block
    - If markers already exist → replace only the block between them
    - If file exists without markers → append the block at the end

    User-written content outside the markers is NEVER touched.
    """
    repo_root = get_repo_root()
    prompts_dir = repo_root / "prompts"

    if not prompts_dir.exists():
        print(colored(f"⚠️  Prompts directory not found at {prompts_dir}", "yellow"))
        print(colored("    Master Prompt not installed. Install manually if needed.", "yellow"))
        return

    # Pick base prompt: Thai uses thai version, others use English canonical
    if language == "th":
        base_file = prompts_dir / "core" / "master_prompt.th.md"
    else:
        base_file = prompts_dir / "core" / "master_prompt.en.md"

    overlay_file = prompts_dir / "method_overlay" / f"method{method}.md"

    if not base_file.exists() or not overlay_file.exists():
        print(colored(f"⚠️  Prompt files missing", "yellow"))
        return

    base = base_file.read_text(encoding="utf-8")
    overlay = overlay_file.read_text(encoding="utf-8")

    # Replace {LANGUAGE} placeholder
    target_lang = get_language(language)
    lang_str = f"{target_lang.english_name} ({target_lang.native_name})"
    base = base.replace("{LANGUAGE}", lang_str)
    overlay = overlay.replace("{LANGUAGE}", lang_str)

    # Build the hookglot block, wrapped in markers
    hookglot_block = (
        f"{HOOKGLOT_MARKER_START}\n\n"
        f"{base}\n\n---\n\n{overlay}\n\n"
        f"{HOOKGLOT_MARKER_END}"
    )

    claude_md = get_claude_md_path()
    claude_md.parent.mkdir(parents=True, exist_ok=True)

    if not claude_md.exists():
        # Fresh install — just write the block
        claude_md.write_text(hookglot_block + "\n", encoding="utf-8")
        print(colored(f"✅ Created CLAUDE.md with hookglot block at {claude_md}", "green"))
        return

    existing = claude_md.read_text(encoding="utf-8")

    if HOOKGLOT_MARKER_START in existing and HOOKGLOT_MARKER_END in existing:
        # Markers exist — replace only the block between them
        start_idx = existing.find(HOOKGLOT_MARKER_START)
        end_idx = existing.find(HOOKGLOT_MARKER_END) + len(HOOKGLOT_MARKER_END)
        new_content = existing[:start_idx] + hookglot_block + existing[end_idx:]
        claude_md.write_text(new_content, encoding="utf-8")
        print(colored(f"✅ Updated hookglot block in CLAUDE.md (your content preserved)", "green"))
    else:
        # No markers — append the block to the existing file
        sep = "\n\n" if existing.rstrip() else ""
        new_content = existing.rstrip() + sep + hookglot_block + "\n"
        claude_md.write_text(new_content, encoding="utf-8")
        print(colored(f"✅ Appended hookglot block to existing CLAUDE.md (your content preserved)", "green"))


def remove_master_prompt_block():
    """Remove only the hookglot block from CLAUDE.md, preserve user content.

    Used by `hookglot switch off` and `hookglot uninstall`.
    """
    claude_md = get_claude_md_path()
    if not claude_md.exists():
        return

    existing = claude_md.read_text(encoding="utf-8")

    if HOOKGLOT_MARKER_START not in existing or HOOKGLOT_MARKER_END not in existing:
        # No markers — leave file alone (user-only content)
        return

    start_idx = existing.find(HOOKGLOT_MARKER_START)
    end_idx = existing.find(HOOKGLOT_MARKER_END) + len(HOOKGLOT_MARKER_END)
    new_content = (existing[:start_idx].rstrip() + "\n" + existing[end_idx:].lstrip()).strip()

    if new_content:
        claude_md.write_text(new_content + "\n", encoding="utf-8")
        print(colored(f"✅ Removed hookglot block from CLAUDE.md (your content preserved)", "green"))
    else:
        # File only contained hookglot block — remove the file entirely
        claude_md.unlink()
        print(colored(f"✅ Removed CLAUDE.md (only contained hookglot block)", "green"))


def cmd_status(args):
    """Show current configuration."""
    config = load_config()
    print(colored("\n🌐 hookglot status\n", "bold"))

    method_names = {1: "Input-only", 2: "Output-only"}

    lang_code = config.get("language", "th")
    lang = LANGUAGES.get(lang_code)
    lang_str = f"{lang.english_name} ({lang.native_name})" if lang else lang_code

    print(f"  Language     : {lang_str} [{lang_code}]")
    print(f"  Method       : {config.get('method')} ({method_names.get(config.get('method'), 'unknown')})")
    print(f"  Translator   : {config.get('translator')}")

    # Provider details
    try:
        pcfg = get_provider_config(config.get("translator"))
        print(f"  Model        : {pcfg.get('model', 'N/A')}")
        if "base_url" in pcfg:
            print(f"  Endpoint     : {pcfg['base_url']}")
    except (ValueError, KeyError):
        pass

    print(f"\n  Config file  : {CONFIG_FILE}")
    print(f"  Settings     : {get_claude_settings_path()}")
    print(f"  Master Prompt: {get_claude_md_path()}")

    # Health check
    print(colored("\nHealth check:", "bold"))
    try:
        load_env()
        translator = get_translator(config.get("translator"), get_provider_config(config.get("translator")))
        if translator.health_check():
            print(colored(f"  ✅ {config.get('translator')} ready", "green"))
        else:
            print(colored(f"  ❌ {config.get('translator')} not reachable", "red"))
    except Exception as e:
        print(colored(f"  ❌ Error: {e}", "red"))


def cmd_switch(args):
    """Switch method or disable hooks."""
    raw = str(args.method).strip().lower()

    if raw in ("off", "0", "disable", "disabled"):
        # Disable mode — keep config but remove hooks from Claude Code
        config = load_config()
        config["method"] = "off"
        save_config(config)

        settings_path = get_claude_settings_path()
        if settings_path.exists():
            is_corrupt = False
            with open(settings_path, "r", encoding="utf-8") as f:
                try:
                    settings = json.load(f)
                except json.JSONDecodeError:
                    is_corrupt = True
                    
            if is_corrupt:
                print(colored(f"\n❌ Error: {settings_path} is not valid JSON.", "red"))
                print(colored("Please fix the file manually to avoid losing your configurations.", "yellow"))
                sys.exit(1)

            # Remove only hookglot's hooks (preserve other user hooks)
            settings = remove_hookglot_hooks_from_settings(settings)
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

        # Remove only the hookglot block from CLAUDE.md (preserve user content)
        remove_master_prompt_block()

        print(colored("✅ hookglot disabled — Claude Code now runs without translation", "green"))
        print(colored("   To re-enable: hookglot switch 1 (or 2)", "cyan"))
        return

    # Numeric method
    try:
        method = int(raw)
    except ValueError:
        print(colored(f"Invalid method: {raw}. Use 1, 2, or off.", "red"))
        sys.exit(1)

    if method not in (1, 2):
        print(colored(f"Invalid method: {method}. Use 1, 2, or off.", "red"))
        sys.exit(1)

    config = load_config()
    config["method"] = method
    save_config(config)

    # Re-install hooks and master prompt for new method
    install_hooks(method)
    install_master_prompt(config["language"], method)

    method_names = {1: "Input-only", 2: "Output-only"}
    print(colored(f"✅ Switched to Method {method} ({method_names[method]})", "green"))

    # Warn if there's a project-level .claude/ that may need updating
    warn_about_project_claude(method)


def cmd_translator(args):
    """Switch translator provider."""
    provider = args.provider.lower()
    if provider not in SUPPORTED_PROVIDERS:
        print(colored(f"Unknown provider: {provider}", "red"))
        print(f"Supported: {', '.join(SUPPORTED_PROVIDERS)}")
        sys.exit(1)

    config = load_config()
    config["translator"] = provider
    save_config(config)
    print(colored(f"✅ Switched translator to {provider}", "green"))

    # Check API key for cloud providers
    if provider != "ollama":
        load_env()
        try:
            pcfg = get_provider_config(provider)
            env_var = pcfg.get("api_key_env", "")
            if env_var and not os.environ.get(env_var):
                print(colored(
                    f"\n⚠️  {env_var} not set. Run: hookglot set-key {provider}",
                    "yellow",
                ))
        except (ValueError, KeyError):
            pass


def cmd_lang(args):
    """Switch language."""
    lang = args.code
    if lang not in LANGUAGES:
        print(colored(f"Unknown language: {lang}", "red"))
        print(f"Supported: {', '.join(LANGUAGES.keys())}")
        sys.exit(1)

    config = load_config()
    config["language"] = lang
    save_config(config)

    # Re-install master prompt for new language
    install_master_prompt(lang, config["method"])

    target_lang = get_language(lang)
    print(colored(
        f"✅ Switched to {target_lang.english_name} ({target_lang.native_name})",
        "green",
    ))


def cmd_set_key(args):
    """Set API key for a provider."""
    provider = args.provider.lower()
    if provider not in SUPPORTED_PROVIDERS:
        print(colored(f"Unknown provider: {provider}", "red"))
        sys.exit(1)
    if provider == "ollama":
        print(colored("Ollama doesn't need an API key", "yellow"))
        return

    pcfg = get_provider_config(provider)
    env_var = pcfg.get("api_key_env", "")

    print(f"Setting {env_var} for {provider}")
    api_key = input("API key: ").strip()
    if not api_key:
        print(colored("Cancelled", "yellow"))
        return

    write_env_file({env_var: api_key})
    print(colored(f"✅ Saved to ~/.hookglot/.env", "green"))


def cmd_test(args):
    """Test translation."""
    config = load_config()
    load_env()

    print(colored("\n🧪 Testing translation...\n", "bold"))

    target_lang = config.get("language", "th")
    provider = config.get("translator", "ollama")

    test_samples = {
        "th": "ช่วยอธิบาย Pass-the-Hash attack หน่อย แล้วใช้ NTLM hash ทำ Privilege Escalation ยังไง",
        "ja": "Pass-the-Hash攻撃について説明してください。NTLMハッシュを使ってPrivilege Escalationを行う方法は?",
        "zh-CN": "请解释Pass-the-Hash攻击,以及如何使用NTLM hash进行Privilege Escalation",
        "zh-TW": "請解釋Pass-the-Hash攻擊,以及如何使用NTLM hash進行Privilege Escalation",
        "ko": "Pass-the-Hash 공격을 설명하고 NTLM hash로 Privilege Escalation을 어떻게 하는지 알려주세요",
        "vi": "Giải thích về Pass-the-Hash attack và cách dùng NTLM hash để Privilege Escalation",
        "id": "Jelaskan Pass-the-Hash attack dan bagaimana menggunakan NTLM hash untuk Privilege Escalation",
        "ms": "Jelaskan Pass-the-Hash attack dan cara menggunakan NTLM hash untuk Privilege Escalation",
    }
    sample = test_samples.get(target_lang, test_samples["th"])

    print(f"Provider: {provider}")
    print(f"Language: {target_lang}")
    print(f"\nInput ({target_lang}):\n  {sample}\n")

    try:
        pcfg = get_provider_config(provider)
        translator = get_translator(provider, pcfg)
    except Exception as e:
        print(colored(f"❌ Setup error: {e}", "red"))
        sys.exit(1)

    if not translator.health_check():
        print(colored(f"❌ {provider} not reachable", "red"))
        sys.exit(1)

    # Test forward translation
    try:
        en = translator.translate(sample, source_lang_code=target_lang, target_lang_code="en")
        print(f"Translated to English:\n  {en}\n")

        # Verify technical terms preserved
        for term in ["Pass-the-Hash", "NTLM", "Privilege Escalation"]:
            if term in en:
                print(colored(f"  ✅ '{term}' preserved", "green"))
            else:
                print(colored(f"  ⚠️  '{term}' may have been altered", "yellow"))
    except Exception as e:
        print(colored(f"❌ Translation failed: {e}", "red"))
        sys.exit(1)

    # Test backward translation with code
    en_with_code = """To perform Pass-the-Hash, run:

```bash
crackmapexec smb 10.10.10.5 -u administrator -H NTLM_HASH
```

The `NOPASSWD` entry in sudoers can be exploited."""

    print(f"\nTesting EN→{target_lang} with code preservation...")
    try:
        back = translator.translate(en_with_code, source_lang_code="en", target_lang_code=target_lang)
        print(f"Translated back:\n{back}\n")

        if "crackmapexec smb 10.10.10.5" in back:
            print(colored("  ✅ Code block preserved", "green"))
        else:
            print(colored("  ⚠️  Code block may be mangled", "yellow"))

        if "NOPASSWD" in back:
            print(colored("  ✅ Inline code preserved", "green"))
        else:
            print(colored("  ⚠️  `NOPASSWD` may be altered", "yellow"))
    except Exception as e:
        print(colored(f"❌ Reverse translation failed: {e}", "red"))

    print(colored("\n✅ Test complete", "green"))


def cmd_uninstall(args):
    """Remove hookglot from Claude Code (preserve other user config)."""
    # 1. Remove our hooks from settings.json (keep other user hooks)
    settings_path = get_claude_settings_path()
    if settings_path.exists():
        is_corrupt = False
        with open(settings_path, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                is_corrupt = True
                
        # แจ้งเตือนและหยุดการทำงานหากไฟล์พัง เพื่อป้องกันข้อมูลของ User หาย
        if is_corrupt:
            print(colored(f"\n❌ Error: {settings_path} is not valid JSON.", "red"))
            print(colored("Please fix the file manually to avoid losing your configurations.", "yellow"))
            sys.exit(1)

        settings = remove_hookglot_hooks_from_settings(settings)
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        print(colored("✅ Hookglot hooks removed (other hooks preserved)", "green"))

        
    # 2. Remove hookglot block from CLAUDE.md (preserve user content)
    remove_master_prompt_block()

    # 3. Remove our slash commands
    cmd_dir = Path.home() / ".claude" / "commands"
    if cmd_dir.exists():
        removed = []
        for f in cmd_dir.glob("hookglot-*.md"):
            try:
                f.unlink()
                removed.append(f.name)
            except OSError:
                pass
        if removed:
            print(colored(f"✅ Removed {len(removed)} slash commands", "green"))

    print(colored(f"\nConfig and API keys still in {CONFIG_DIR}", "cyan"))
    print(colored("(delete manually if you want to fully remove hookglot)", "cyan"))


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    # Force UTF-8 stdout/stderr — fixes emoji rendering on Windows console
    # where default codepage (cp1252/cp874/etc.) can't encode 🌐 ✅ etc.
    # This makes the CLI work consistently across bash, cmd, PowerShell.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(
        prog="hookglot",
        description="Translation hooks for Claude Code",
    )
    parser.add_argument("--version", action="version", version=f"hookglot {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=False)

    p_install = subparsers.add_parser("install", help="Interactive setup")

    p_status = subparsers.add_parser("status", help="Show current configuration")

    p_switch = subparsers.add_parser("switch", help="Switch translation method (1, 2, or off)")
    p_switch.add_argument("method", help="Method: 1 = input-only, 2 = output-only, off = disable hooks")

    p_trans = subparsers.add_parser("translator", help="Switch translator provider")
    p_trans.add_argument("provider", help="Provider name")

    p_lang = subparsers.add_parser("lang", help="Switch language")
    p_lang.add_argument("code", help="Language code (e.g., th, ja, zh-CN)")

    p_key = subparsers.add_parser("set-key", help="Set API key for a provider")
    p_key.add_argument("provider", help="Provider name")

    p_test = subparsers.add_parser("test", help="Test translation")

    p_uninstall = subparsers.add_parser("uninstall", help="Remove hooks from Claude Code")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "install": cmd_install,
        "status": cmd_status,
        "switch": cmd_switch,
        "translator": cmd_translator,
        "lang": cmd_lang,
        "set-key": cmd_set_key,
        "test": cmd_test,
        "uninstall": cmd_uninstall,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
