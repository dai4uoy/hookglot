---
description: Switch hookglot translation provider
argument-hint: <ollama | openai | anthropic | google | deepseek | alibaba | moonshot | zhipu | nvidia>
allowed-tools: Bash
---

Use the Bash tool to run:

```
hookglot translator $ARGUMENTS
```

The bash output is automatically displayed by Claude Code. Do NOT repeat it.

Your text response must be EXACTLY this and nothing more:

```
[hg-bypass]

Type /clear to apply.
```

If the bash output mentioned a missing API key, append one extra line:
"Run `hookglot set-key $ARGUMENTS` to add the API key."

Otherwise stop after the /clear line. No echo, no summary.
