# Translation Methods

hookglot supports 3 translation methods. Pick based on your priorities.

## Method 1: Two-Way (input + output)

```
You (Thai) ──hook──► English ──► Claude ──► English ──hook──► Thai (you see)
```

**When to use:**
- You want maximum token savings
- You're paying per-token (Anthropic API direct)
- Output responses are typically very long
- You can tolerate seeing English then translation

**Pros:**
- ✅ ~30-50% token savings
- ✅ Claude reasons in English (often clearer)

**Cons:**
- ❌ UX: English streams first, then translation appears below
- ❌ Output translation can sometimes mangle markdown/code (rare)
- ❌ 2x translation latency

**Switch:** `hookglot switch 1`

---

## Method 2: One-Way (input only) ⭐ Default

```
You (Thai) ──hook──► English ──► Claude ──► Thai (you see directly)
```

**When to use:**
- You want best output quality
- You're on a Claude Code subscription (no per-token cost)
- You prefer simpler UX (just see Thai)
- Working with code-heavy content where output translation risk matters

**Pros:**
- ✅ Cleanest UX (only see Thai)
- ✅ Output quality untouched (Claude writes Thai directly)
- ✅ Lower latency (only input translation)
- ✅ Safe for code/commands (no risk of mangling)

**Cons:**
- ❌ Less token savings (~10-20%, mostly input side)

**Switch:** `hookglot switch 2`

---

## Method 3: Output-Only

```
You (Thai) ──────────► Claude (Master Prompt forces EN) ──► English ──hook──► Thai (you see)
```

**When to use:**
- You want maximum token savings (similar to Method 1 in cost)
- You're OK with English visible above translation
- You don't mind that Claude sometimes ignores Master Prompt and answers in Thai

**Pros:**
- ✅ Maximum output token savings
- ✅ Claude doesn't see translation overhead in input

**Cons:**
- ❌ UX: same as Method 1 — see English then Thai
- ❌ Master Prompt enforcement is best-effort (LLM autonomy)
- ❌ Same code mangling risk as Method 1

**Switch:** `hookglot switch 3`

---

## Quick Comparison

| | Method 1 | Method 2 | Method 3 |
|---|---|---|---|
| Input translation | ✅ | ✅ | ❌ |
| Output translation | ✅ | ❌ | ✅ |
| Claude responds in | English | Local lang | English |
| Token savings | ~30-50% | ~10-20% | ~30-50% |
| UX cleanliness | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Output quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Code safety | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**TL;DR:** Method 2 is the recommended default. Switch to 1 or 3 only if you really need the token savings.
