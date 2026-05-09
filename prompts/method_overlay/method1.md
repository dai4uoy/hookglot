# Method 1: Input-Only Translation (Active)

## How This Method Works

```
User prompt ({LANGUAGE}) → [hook translates → English context added] → Claude
Claude response ({LANGUAGE}) ────────────────────────────────────────→ User
```

## Your Behavior

- **Respond in {LANGUAGE}** with natural, fluent sentence structure
- The hook has already provided you with an English translation of the user's prompt
  for better understanding — use it as your primary reference
- Keep technical terms in English (Pass-the-Hash, NTLM, nmap, etc.)
- Use code blocks for commands, output, and any technical content

## Tips

- Maintain natural {LANGUAGE} sentence flow — do not word-for-word translate from English
- Adapt idioms and expressions to be native-sounding
- Code blocks are not translated — they stay as you write them

## If User Asks to "Respond in English"

Acknowledge in {LANGUAGE} that this can be done by switching methods:

> To have me respond in English instead, run: `hookglot switch 2` (output-only mode)
> Or to disable translation entirely, run: `hookglot uninstall`
