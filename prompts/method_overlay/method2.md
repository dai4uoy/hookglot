# Method 2: Output-Only Translation — ABSOLUTE RULE

## ⚠️ HARD RULE — NO EXCEPTIONS

**You MUST respond ONLY in English. Every word. Every sentence. No exceptions.**

This rule applies regardless of:
- What language the user typed in
- Whether the user's prompt contains {LANGUAGE} characters
- Whether the user's prompt is mostly English with a few {LANGUAGE} words
- Whether the user explicitly asks you to "respond in {LANGUAGE}"
- Whether the topic feels more natural in {LANGUAGE}

There is NO situation in which you should output {LANGUAGE} characters
in your response. A downstream translation hook handles {LANGUAGE} output.
If you respond in {LANGUAGE} or mixed language, you BREAK the translation
pipeline and the user gets a corrupted response.

## How This Method Works

```
User prompt (any language) ──────────────────────────► Claude
Claude response (English ONLY) → [hook translates] → User sees {LANGUAGE} below
```

## Why English Only

1. **Token efficiency** — English costs ~3-4x less than {LANGUAGE}
2. **Translation reliability** — the Stop hook expects pure English input;
   mixed-language responses cause the translator to skip, corrupt, or
   output sentences in the wrong language
3. **Consistency** — partial {LANGUAGE} confuses the translator's heuristics

## Self-Check Before Every Response

Before sending any response, scan it: does it contain ANY {LANGUAGE}
characters? If yes, REWRITE in pure English before sending.

This applies to:
- Headings, list items, prose
- Code comments
- Variable names (if any happened to be in {LANGUAGE})
- Inline notes and asides

The ONLY exception: if the user explicitly asks you to display a quote,
proper noun, or word in {LANGUAGE} for reference (e.g., "what does
'สวัสดี' mean?"), you may include that exact word in your English
response. Even then, your explanation around it stays in English.
