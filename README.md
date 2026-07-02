# 🌐 hookglot

> Translation hooks for Claude Code — cut Anthropic-side token cost for non-English users while you keep typing in your own language 🌐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange.svg)](https://claude.com/claude-code)
[![Cross-platform](https://img.shields.io/badge/OS-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](#)
[![Version](https://img.shields.io/badge/version-1.5.0-success.svg)](CHANGELOG.md)

**hookglot** intercepts the prompts and responses flowing through Claude Code and translates them automatically via your choice of LLM provider — local (Ollama) or cloud (9 providers). Type in your native language, save tokens, get answers.

📖 **อ่านเป็นภาษาไทย**: [README.th.md](README.th.md)

---

---


https://github.com/user-attachments/assets/080a1f3a-03e1-410a-a985-7c301509fc7c


---

---

## ✨ Features

- 🎯 **2 Translation Methods** — input-only or output-only (with disable mode)
- 🌏 **8 Asian Languages** — Thai, Japanese, Chinese (Simplified/Traditional), Korean, Vietnamese, Indonesian, Malay
- 🤖 **9 Translation Providers** — Ollama (default, free), OpenAI, Anthropic, Google, DeepSeek, Alibaba, Moonshot, Zhipu, NVIDIA
- 🛡️ **Format Preservation** — code blocks, URLs, IPs, env vars stay intact through translation
- 💬 **Bilingual Logging** — translated log plus an English-original log, organized by date and an AI-generated session title
- 🎮 **Slash Commands** — switch settings without leaving Claude Code (`/hookglot-method`, `/hookglot-translator`, `/hookglot-off`, etc.)
- ✅ **Safe Install** — preserves your existing Claude Code hooks, memory, and slash commands

---

## 🎬 How It Works

```
Method 1 (Input-only) Recommended for create a documents/reports
   Native prompt ──► [hook translates → English] ──► Claude
                                                       │
   Native response ◄──────────────────────────────────┘ (Claude responds in your language)

Method 2 (Output-only) — best token savings
   Native prompt ────────────────────────────────► Claude (overlay enforces English)
                                                       │
   English response shown in Claude Code               │
                                                       ▼
                                          [Stop hook translates → Native]
                                                       │
                                                       ▼
                          Native log → ~/.hookglot/conversations/<dd.mm.yy>/<title>.md
                          English log → ~/.hookglot/conversation_en.md
                          (translation NOT injected inline by default — avoids token leak)
```

**Which to pick?** Method 2 saves the most tokens (Claude answers in token-cheap
English, the provider translates). Method 1 is better when you want Claude to
*write files* (reports, docs) directly in your language, since the hook only
translates the response stream, not files on disk.

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

### 📖 Viewing translated responses

For **Method 2**, translations are written to files (not injected inline — see
[Limitations](#-limitations)):

- `~/.hookglot/conversations/<dd.mm.yy>/<ai-title>.md` — per-session, organized by date with an AI-generated title
- `~/.hookglot/conversation.md` — cumulative translated log (clearable via `/hookglot-clear-chat`)
- `~/.hookglot/conversation_en.md` — cumulative **English original** log (handy for exporting English reports or comparing the translation)

```bash
hookglot start              # Launches grip + browser (recommended)
/hookglot-start             # Same, from inside Claude Code

# Or manually:
grip ~/.hookglot/conversation.md           # Run grip yourself
code ~/.hookglot/conversation.md           # VSCode markdown preview

# Live tail (separate terminal):
tail -f ~/.hookglot/conversation.md        # Linux/Mac
Get-Content ~/.hookglot/conversation.md -Wait -Tail 0    # PowerShell
```

#### Optional: inline display

You can opt in to showing the translation inline in Claude Code:

```bash
hookglot switch 2 --output on     # show translation inline (off by default)
```

This is **off by default** because inline display writes the translation into
Claude Code's transcript. The harness filters most of it back out, but keeping it
off guarantees zero leak and the fastest turns.

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
| `/hookglot-clear-chat`      | Clear the conversation logs  |
| `/hookglot-test`            | Test translation pipeline    |

After a method or language switch, type `/clear` to start a fresh session for the
change to take effect. (Toggling `--output` does **not** require `/clear` — the
hook reads it live each turn.)

---

## 🛠️ CLI Commands (terminal)

```bash
hookglot install              # Interactive setup
hookglot status               # Show current configuration
hookglot switch 1|2|off       # Switch method or disable
hookglot switch 2 --output on # Toggle inline translation display
hookglot translator <name>    # Switch provider
hookglot lang <code>          # Switch language
hookglot set-key <provider>   # Set API key
hookglot clear-chat           # Clear conversation logs
hookglot test                 # Test translation
hookglot uninstall            # Remove hookglot (preserves other config)
```

---

## 📊 Benchmarks

Method 2 saves Anthropic-side tokens because Claude answers in **English** — which
tokenizes far cheaper than Thai (~2.8 vs ~1.3 chars/token) — and the translation
to Thai happens at the provider (e.g. DeepSeek), not Anthropic.

A 5-prompt set of universal CS questions (turns 2–5, Opus 4.8), compared
mode-to-mode:

| Mode | Out tok | Cost | vs native |
|------|--------:|-----:|----------:|
| native (Thai) | 7,667 | $0.2841 | base |
| native_en | 5,077 | $0.2091 | −26% |
| **hookglot** | 5,305 | $0.1894 | **−33%** |
| hookglot + caveman | 2,663 | $0.1165 | −59% |

Savings scale with how much Thai the native baseline would naturally produce —
conversational questions save more, English-heavy technical ones save less.

➡️ Full methodology and how to reproduce: [**docs/benchmark.md**](docs/benchmark.md)

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

> **Tip:** if a hook fires but no translation appears, run Claude Code from a
> sub-folder (e.g. `~/work`) rather than your home directory directly. When the
> working directory *is* your home, `~/.claude` sits under it and Claude Code's
> file-snapshotting can race the hook. hookglot retries the transcript read to
> mitigate this, but a sub-folder avoids it entirely.

---

## 🛡️ Format Preservation

hookglot uses 3-layer format protection so technical content stays intact through translation:

1. **Code Block Extraction** — `` ```code``` `` and `` `inline` `` preserved verbatim, and re-inserted on their own lines so a translated fence never glues onto prose
2. **Aggressive Element Protection** — URLs, IPs, emails, env vars, file paths, hashes, constants stay untouched
3. **Strict Translator Prompts** — explicit instructions to maintain Markdown structure

Result: ~90-95% format reliability for typical use.

---

## 📚 Documentation

- [**Methods**](docs/methods.md) — When to use each translation method
- [**Providers**](docs/providers.md) — Setup guide for all 9 providers
- [**Languages**](docs/languages.md) — Supported languages and language codes
- [**Architecture**](docs/architecture.md) — How hooks work internally
- [**Benchmark**](docs/benchmark.md) — Measuring token savings reliably
- [**Troubleshooting**](docs/troubleshooting.md) — Common issues and fixes

---

## ⚠️ Limitations

- **No inline translation display by default**: translations are saved to files and viewable via `hookglot start` (grip) or any markdown editor. Inline display is opt-in (`--output on`) because it writes translations into Anthropic's transcript. Saving to file keeps the leak at zero.
- **Method 2 writes files in English**: the Stop hook translates the response *stream*, not files Claude creates on disk. If Claude writes a report/`.docx`/`.pdf`, it stays English. Use **Method 1** when you need Claude to author files directly in your language.
- **Transcript schema is version-coupled**: hookglot parses Claude Code's transcript `.jsonl`, whose structure changes between releases. Re-verify after a Claude Code update if hooks stop producing output.
- **Long agentic turns can hit translation timeouts**: very long responses may exceed the provider's read timeout (English shown, error noted). Raise `timeout` under your provider in `~/.hookglot/config.yaml`.
- **First Ollama call**: ~5-10s while the model loads into RAM.
- **No quota fallback**: when a cloud provider's quota runs out you get a notification — no automatic switching.
- **Project-level settings**: must be configured manually (snippet provided).
- **Claude occasionally ignores the overlay**: for Method 2, Claude may respond in mixed languages despite instructions. A defensive check catches most cases but not all — an LLM autonomy limit.
- **Cross-platform testing**: heavily tested on Windows + Python 3.14 and on Linux (Kali). macOS should work (same `pathlib`, `subprocess`, stdlib) but is less verified.

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
- [DeepSeek](https://platform.deepseek.com) for an excellent multilingual model
