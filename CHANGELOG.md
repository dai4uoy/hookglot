# Changelog

All notable changes to hookglot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
