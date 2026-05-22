# Architecture

How hookglot works internally.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Claude Code                             │
│                                                                 │
│   User Input ──────────────────► [UserPromptSubmit Hook] ───┐  │
│                                                              │  │
│                                                              ▼  │
│                                                         ┌────────┐
│                                                         │ Claude │
│                                                         │  LLM   │
│                                                         └────┬───┘
│                                                              │  │
│   User Display ◄───── [Stop Hook] ◄───── Response ◄──────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ JSON via stdin/stdout
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          hookglot                               │
│                                                                 │
│  ┌─────────────────┐    ┌────────────────────┐                 │
│  │  hooks/         │    │  config.py         │                 │
│  │  ├ translate_   │◄───┤  ~/.hookglot/      │                 │
│  │  │  input.py    │    │     config.yaml    │                 │
│  │  └ translate_   │    │     .env           │                 │
│  │     output.py   │    └────────────────────┘                 │
│  └─────┬───────────┘                                            │
│        │                                                        │
│        ▼                                                        │
│  ┌─────────────────┐    ┌────────────────────┐                 │
│  │ format_         │    │ translators/       │                 │
│  │ preservation.py │───►│  ├ ollama          │                 │
│  │ (placeholders)  │    │  ├ openai_compat   │                 │
│  └─────────────────┘    │  ├ anthropic       │                 │
│                          │  └ google          │                 │
│                          └────┬───────────────┘                 │
└────────────────────────────────┼───────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ Translation Provider   │
                    │ (Ollama / OpenAI /     │
                    │  Anthropic / Google /  │
                    │  DeepSeek / Alibaba /  │
                    │  Moonshot / Zhipu /    │
                    │  NVIDIA)               │
                    └────────────────────────┘
```

## Data Flow

### UserPromptSubmit Hook (Methods 1, 2)

1. User types prompt in Claude Code
2. Claude Code pauses, calls `python3 -m hookglot.hooks.translate_input`
3. Hook reads JSON from stdin: `{"prompt": "...", "transcript_path": "..."}`
4. Hook checks config: target language, translator provider
5. Hook detects if prompt contains target-language characters
6. If yes, hook calls translator → English
7. Hook outputs JSON to stdout: `{"hookSpecificOutput": {"additionalContext": "..."}}`
8. Claude Code prepends this context to the prompt sent to Claude

### Stop Hook (Methods 1, 3)

1. Claude finishes generating response (already streamed to user)
2. Claude Code calls `python3 -m hookglot.hooks.translate_output`
3. Hook reads JSON from stdin (transcript path included)
4. Hook parses transcript JSONL to find last assistant message
5. Hook calls translator → target language
6. Hook prints translation to stderr (Claude Code displays it)

## Format Preservation

```
Original text:
"Use ```bash\ncrackmapexec smb 10.10.10.5\n``` to test the host. Visit https://example.com"

Step 1: Extract preservable elements
preserved = {
    "⟨⟨CODE_0⟩⟩": "```bash\ncrackmapexec smb 10.10.10.5\n```",
    "⟨⟨IPV4_1⟩⟩": "10.10.10.5",
    "⟨⟨URL_2⟩⟩": "https://example.com",
}

Working text:
"Use ⟨⟨CODE_0⟩⟩ to test the host. Visit ⟨⟨URL_2⟩⟩"

Step 2: Send to translator
"ใช้ ⟨⟨CODE_0⟩⟩ เพื่อทดสอบ host เข้าไปที่ ⟨⟨URL_2⟩⟩"

Step 3: Restore placeholders
"ใช้ ```bash\ncrackmapexec smb 10.10.10.5\n``` เพื่อทดสอบ host เข้าไปที่ https://example.com"
```

## Configuration

Config lives in `~/.hookglot/`:

```
~/.hookglot/
├── config.yaml       # Method, language, provider, model selection
└── .env              # API keys (chmod 600)
```

Hooks register in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "..."}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "..."}]}]
  }
}
```

Master Prompt installs at `~/.claude/CLAUDE.md` (Claude Code reads this each session).

## Why This Architecture?

**Why hooks instead of MCP?** Hooks intercept at the right point — before Claude
sees input and after Claude generates output. MCP tools require Claude to *choose*
to use them, which isn't reliable for pre/post processing.

**Why not modify Claude Code itself?** Claude Code's design is intentionally minimal.
Hooks are the official extension mechanism.

**Why placeholders for code preservation?** LLMs are stochastic. Even with strict
prompts, they'll occasionally translate code. Placeholders force deterministic
preservation.

**Why no fallback chain?** Auto-fallback creates surprise behavior (cost, quality).
Manual switching keeps user in control. If primary fails, user sees a clear notification.
