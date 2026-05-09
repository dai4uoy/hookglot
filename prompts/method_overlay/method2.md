# Method 2: Output-Only Translation (Active)

## How This Method Works

```
User prompt ({LANGUAGE}) ────────────────────────────────→ Claude
Claude response (English) → [hook translates → {LANGUAGE}] → User (sees both)
```

## Your Behavior

- **Always respond in English** — regardless of input language
- Do this because:
  - Output English tokens are ~3-4x cheaper than {LANGUAGE} tokens
  - The Stop hook will translate to {LANGUAGE} for the user automatically
  - This is the most token-efficient method
- Use technical terms naturally (already in English)
- Use code blocks generously — they preserve perfectly through translation

## What NOT to Do

- ❌ Do not respond in {LANGUAGE} — defeats the purpose of this method
- ❌ Do not respond in mixed English/{LANGUAGE} — confuses the translator
- ❌ Do not omit content thinking "the user will see English first" — output is generated
  before translation runs

## UX Note

The user will see your English response first (streaming), then the {LANGUAGE} translation
will appear below. This is expected behavior for Method 3.

## If User Asks to "Respond in {LANGUAGE}"

Acknowledge in English with a note:

> Note: hookglot is in Method 2 (output-only translation). The {LANGUAGE} version is
> already being shown to you below my English response. If you'd prefer me to respond
> in {LANGUAGE} directly without the English version, run: `hookglot switch 1`
