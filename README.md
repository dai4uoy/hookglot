# 🌐 hookglot

> Translation hooks for Claude Code — speak your language, save your tokens

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange.svg)](https://claude.com/claude-code)
[![Cross-platform](https://img.shields.io/badge/OS-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](#)
[![Version](https://img.shields.io/badge/version-1.2.0-success.svg)](CHANGELOG.md)

**hookglot** intercepts your prompts to/from Claude Code and translates them automatically through your choice of LLM provider — local (Ollama) or cloud (9 providers supported). Type in your native language, save tokens, get answers.

📖 **อ่านเป็นภาษาไทย**: [README.th.md](README.th.md)

---

## ✨ Features

- 🎯 **2 Translation Methods** — input-only or output-only (with disable mode)
- 🌏 **8 Asian Languages** — Thai, Japanese, Chinese (Simplified/Traditional), Korean, Vietnamese, Indonesian, Malay
- 🤖 **9 Translation Providers** — Ollama (default, free), OpenAI, Anthropic, Google, DeepSeek, Alibaba, Moonshot, Zhipu, NVIDIA
- 🛡️ **Smart Format Preservation** — code blocks, URLs, IPs, env vars stay intact through translation
- 🎮 **Slash Commands** — switch settings without leaving Claude Code (`/hookglot-method`, `/hookglot-translator`, `/hookglot-off`, etc.)
- 🔒 **Privacy-First** — Ollama keeps everything local
- ✅ **Safe Install** — preserves your existing Claude Code hooks, memory, and slash commands

---

## 🎬 How It Works

```
Method 1 (Input-only) ⭐ Recommended
   Native prompt ──► [hook translates → English] ──► Claude
                                                       │
   Native response ◄──────────────────────────────────┘ (Claude responds in your language)

Method 2 (Output-only)
   Native prompt ────────────────────────────────► Claude (Master Prompt forces English)
                                                       │
   English + Translation ◄── [hook translates] ◄──────┘
```

---

## 🚀 Quick Start

### Installation

**macOS / Linux:**
```bash
git clone https://github.com/dai4uoy/hookglot.git
cd hookglot
pip install -e .
hookglot install
```

**Windows (CMD or PowerShell):**
```bat
git clone https://github.com/dai4uoy/hookglot.git
cd hookglot
python -m pip install -e .
python -m hookglot install
```

The installer will:
1. Choose your language (Thai, Japanese, Chinese, Korean, etc.)
2. Choose method (input-only or output-only)
3. Choose translator (Ollama, DeepSeek, OpenAI, etc.)
4. Set up API key (if cloud provider)
5. Optionally enter a custom model name (or use default)
6. Configure hooks safely (preserves your other Claude Code config)

### First Use

```bash
hookglot test         # verify translation works
claude                # use Claude Code as usual — translation is automatic
```

---

## 🎮 Slash Commands (inside Claude Code)

After installation, these work directly inside `claude`:

| Command | Description                                      |
|---------|--------------------------------------------------|
| `/hookglot-status`          | Show current configuration   |
| `/hookglot-method 1`        | Switch to input-only mode    |
| `/hookglot-method 2`        | Switch to output-only mode   |
| `/hookglot-off`             | Disable hookglot temporarily |
| `/hookglot-translator kimi` | Switch translator provider   |
| `/hookglot-lang ja`         | Switch target language       |
| `/hookglot-test`            | Test translation pipeline    |

After any switch, type `/clear` to start a fresh session for the change to take effect.

---

## 🛠️ CLI Commands (terminal)

```bash
hookglot install              # Interactive setup
hookglot status               # Show current configuration
hookglot switch 1|2|off       # Switch method or disable
hookglot translator <name>    # Switch provider
hookglot lang <code>          # Switch language
hookglot set-key <provider>   # Set API key
hookglot test                 # Test translation
hookglot uninstall            # Remove hookglot (preserves other config)
```

---

## 🌍 Supported Languages

| Code    | Language       | Native           |
|---------|----------------|------------------|
| `th`    | Thai           | ภาษาไทย          |
| `ja`    | Japanese       | 日本語            |
| `zh-CN` | Chinese (Simp) | 简体中文          |
| `zh-TW` | Chinese (Trad) | 繁體中文          |
| `ko`    | Korean         | 한국어            |
| `vi`    | Vietnamese     | Tiếng Việt       |
| `id`    | Indonesian     | Bahasa Indonesia |
| `ms`    | Malay          | Bahasa Melayu    |


---

## 🛡️ Safe Install Guarantees

hookglot is designed to coexist with your existing Claude Code setup:

- **Your other hooks are preserved** — installing hookglot does NOT overwrite hooks you already have for `Stop`, `UserPromptSubmit`, or any other event. They're merged side by side.
- **Your memory in `CLAUDE.md` is preserved** — hookglot uses markers (`<!-- HOOKGLOT-START -->` ... `<!-- HOOKGLOT-END -->`) so it only touches its own block.
- **Your other slash commands are preserved** — uninstall removes only `hookglot-*.md`, leaving your custom commands intact.

---

## 📂 Project-Level Claude Settings

Claude Code lets each project have its own `.claude/settings.json` that overrides global settings. If you have one, hookglot's global hooks won't fire in that project.

When you run `hookglot install` or `hookglot switch`, hookglot detects this and shows a snippet you can add to the project's settings:

```
⚠️  Project-level settings detected:
     /path/to/project/.claude/settings.json

   If hookglot doesn't work in this project, add this to that file's
   "hooks" → "Stop" array:

     {
       "hooks": {
         "Stop": [{
           "hooks": [{
             "type": "command",
             "command": "/your/python -m hookglot.hooks.translate_output",
             "timeout": 90
           }]
         }]
       }
     }
```

The snippet uses your actual Python path (no manual editing needed).

---

## 🛡️ Format Preservation

hookglot uses 3-layer format protection so technical content stays intact through translation:

1. **Code Block Extraction** — `\`\`\`code\`\`\`` and `` `inline` `` preserved verbatim
2. **Aggressive Element Protection** — URLs, IPs, emails, env vars, file paths, hashes, constants stay untouched
3. **Strict Translator Prompts** — explicit instructions to maintain Markdown structure

Result: ~90-95% format reliability for typical use.

---

## 📚 Documentation

- [**Methods**](docs/methods.md) — When to use each translation method
- [**Providers**](docs/providers.md) — Setup guide for all 9 providers
- [**Languages**](docs/languages.md) — Supported languages and language codes
- [**Architecture**](docs/architecture.md) — How hooks work internally
- [**Troubleshooting**](docs/troubleshooting.md) — Common issues and fixes

---

## ⚠️ Limitations

- **Method 2 streaming UX**: Claude streams English first, translation appears below
- **First Ollama call**: ~5-10s while model loads into RAM
- **No quota fallback**: When a cloud provider's quota runs out, you get a notification — no automatic switching
- **Project-level settings**: must be configured manually (snippet provided)

---

## 🤝 Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Help wanted on:
- Additional language support
- More translator providers
- Better format preservation
- Tests, documentation translations

---

## 📜 License

MIT © 2026 hookglot contributors

---

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude Code and the hooks system
- [Ollama](https://ollama.com) for accessible local LLMs
- [Qwen](https://github.com/QwenLM/Qwen) for excellent multilingual model
