# Changelog

All notable changes to hookglot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0-beta] - 2026

### Added
- **`hookglot start` CLI command** — launches grip server (renders `conversation.md` like GitHub) and opens browser automatically. Grip runs detached so terminal returns immediately.
- **`/hookglot-start` slash command** — same as CLI but invokable from inside Claude Code.
- **Auto-install of `grip`** during `hookglot install` — no manual setup needed.
- **Usage guide** displayed after install — explains how to view conversation logs (CLI, slash, manual).

### Why this matters
Until now, viewing `conversation.md` meant manually opening the file in an editor.
With grip integration, you can read your full translated chat history in a GitHub-style
rendered view directly in your browser, with one command.

### Stop grip server
```
# Windows
taskkill /F /PID <pid_shown_when_started>

# macOS / Linux
kill <pid>
```

### Default port
`http://localhost:6419/`

---


## [1.4.2-beta] - 2026

### Verified
- **No transcript leak** — Comprehensive testing across multiple sessions confirmed
  v1.4.x does NOT inject Thai translations into Claude Code transcript.
  Previous v1.3.0 sessions had `hook_success` attachments containing systemMessage
  output (verified via transcript jsonl analysis) — v1.4.x cleanly removes this.

### Changed
- Stop hook output now uses `sys.stderr` exclusively (no `sys.stdout` JSON output).
  Per Anthropic docs, stderr from Stop hooks is NOT added to model context.
  Display behavior may vary by terminal — translations always saved to
  `conversation.md` regardless of CLI display.

### Notes for users
- "running stop hook · ↓ X tokens" displayed by Claude Code UI during hook
  execution is **NOT Anthropic billing** — it's an estimated/display counter.
  Verify actual cost with `/cost` command.
- `/context` command itself adds ~2k+ tokens to Messages per invocation
  (Claude Code default behavior, unrelated to hookglot).

---

## [1.4.0-beta] - 2026

### 🔴 Critical Token Bug Fixes

**Why this release matters**: v1.1.0–v1.3.0 had a latent bug that re-injected
translated text into Claude's context, doubling Anthropic token usage instead
of saving it. v1.4.0 fixes this and trims other token waste.

### Fixed
- **systemMessage re-inject bug** (translate_output.py): Stop hook was emitting
  the translated text as a JSON `systemMessage` to stdout, which Claude Code
  fed back into Anthropic context every turn. Removed. Effect: **~60% reduction
  in Anthropic tokens for Method 2**. (Bug introduced in v1.1.0, amplified by
  v1.3.0's walk-back logic which made translated text larger.)
- **Duplicate INSTRUCTIONS in additionalContext** (translate_input.py): Method 1
  input hook was injecting behavior rules that already exist in Master Prompt.
  Trimmed context from ~80 tokens to ~20 tokens. Effect: **~5-8% reduction in
  Method 1 input tokens**.

### Changed
- `MAX_CHARS_TO_TRANSLATE` reduced 20k → 12k to cap DeepSeek cost on very long
  responses (negligible loss of content — long responses are rare and the cap
  triggers fallback to last-block-only translation).

### Token Economics After Fix

| Layer | Before v1.4 | After v1.4 |
|-------|-------------|------------|
| Anthropic per Method 2 turn | ~2250 tokens | ~750 tokens |
| Anthropic per Method 1 turn | ~600 tokens | ~560 tokens |
| DeepSeek per translation | unchanged | unchanged |

---

## [1.3.0-beta] - 2026

### Added
- **Conversation logging** — every translated turn is appended to `~/.hookglot/conversation.md`
  for later review. Works for both Method 1 and Method 2.
- **`hookglot clear-chat` CLI command** and `/hookglot-clear-chat` slash command — clear the conversation log
- **Method 1 now installs Stop hook too** (silent, logging-only)
- **Walk-back transcript reading** — Stop hook now collects ALL assistant blocks from the current turn,
  not just the last one. Fixes bug where multi-block responses (e.g., analysis + follow-up question)
  only had the last block translated.

### Changed
- Stop hook safety guards: max 100 lookback lines, max 10 blocks per turn, max 20k chars to translate
- `last_translation.md` is now `conversation.md` (cumulative log instead of overwrite)

### Fixed
- Multi-block assistant responses no longer lose content during translation
- tool_result entries (which have `role: user` in transcript) no longer confuse boundary detection

## [1.2.0] - 2026

### Added
- **Custom model selection during install** — users can now type a custom model
  name when installing/configuring a provider, with fallback to the default
- **Project-level `.claude/` warning** — installer detects and warns when working
  directory has its own `.claude/` that may override global hookglot config
- **Safe hook merging** — hookglot's hooks now merge alongside other user hooks
  in `settings.json` instead of replacing the entire `hooks` block. Other user
  hooks for the same events (UserPromptSubmit, Stop) are preserved.
- **Visual separation in Stop says** — translation output now has blank lines
  before/after for clearer visual separation from Claude's main response
- **Slash commands no longer echo bash output** — slash commands now produce
  cleaner output with just `[hg-bypass]` marker, avoiding duplication since
  Claude Code already shows bash output automatically

### Changed
- **Uninstall is now safer** — only removes hookglot's own hooks/slash commands,
  preserves all other user hooks and customizations
- **Settings.json no longer creates `.json.backup` clutter** — uses safe in-place
  merge instead of backup-and-replace

### Fixed
- Eliminated redundant slash command output that showed bash output twice
- Stop hook output now has proper visual separation in Claude Code UI

## [1.1.0] - 2026

### Changed
- **BREAKING**: Removed Method 1 (two-way translation) — was unreliable as Claude
  often ignored Master Prompt and responded in target language anyway, causing
  the Stop hook to incorrectly translate Thai→English
- **BREAKING**: Renumbered methods. Method 1 = Input-only (was Method 2),
  Method 2 = Output-only (was Method 3)
- Stop hook output is now minimal — no flag emoji, no separator borders, no
  filename note. Translation blends with Claude's native response style.

### Added
- 5 slash commands installed at `~/.claude/commands/`:
  `/hookglot-method`, `/hookglot-translator`, `/hookglot-lang`,
  `/hookglot-status`, `/hookglot-test` — switch settings without leaving Claude
- Debug logging in input hook (was only in output hook)
- Hook entry log on every invocation for easier troubleshooting

## [1.0.0] - 2025

### Added
- Initial release
- 3 translation methods (two-way, input-only, output-only)
- 9 translation providers (Ollama, OpenAI, Anthropic, Google, DeepSeek,
  Alibaba, Moonshot, Zhipu, NVIDIA)
- 8 Asian languages (Thai, Japanese, Chinese Simplified/Traditional, Korean,
  Vietnamese, Indonesian, Malay)
- Format preservation (code blocks, URLs, IPs, emails, env vars, paths, hashes)
- CLI commands: install, status, switch, translator, lang, set-key, test, uninstall
- Master Prompt overlay system (canonical EN + Thai override + per-method overlays)
- Manual translator switching with notify-only failure mode
- Cross-platform support: macOS, Linux, Windows native (uses sys.executable
  for Python detection, skips chmod on Windows)
- PowerShell installation script for Windows users
- CI testing on Ubuntu, macOS, and Windows across Python 3.10/3.11/3.12
- Thai (ภาษาไทย) README translation
- Comprehensive documentation
