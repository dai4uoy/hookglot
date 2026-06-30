# 📊 Benchmarking hookglot

How to measure hookglot's effect on Anthropic-side token cost — and how to do it
*reliably*, because most naïve measurements are distorted by cache noise, wrong
pricing, or the wrong metric.

`benchmark.py` reads Claude Code transcript `.jsonl` files and compares any number
of run "modes" side by side.

---

## Why a careful method matters

LLM cost numbers are easy to get wrong. Three traps dominate:

1. **Cache warm/cold luck** — turn 1 writes the system prompt + `CLAUDE.md` into
   cache. Whether that's a cold write or a warm hit depends on the 5-minute cache
   TTL (did another session prime it recently?). This has nothing to do with the
   mode being tested.
2. **`/cost` ≠ transcript** — Claude Code's `/cost` includes the whole session:
   haiku side-calls for titles, quota checks, and turn 1. None of that is in the
   transcript a script can read, so a script will always read *lower* than `/cost`.
3. **Character count is not content length** — across languages, character count
   reflects script density, not how much was said. Thai is character-dense (~1.3
   chars/token); English is character-light (~2.8 chars/token). hookglot can show
   **+30% characters while costing less**.

---

## The modes

| Mode | Description |
|------|-------------|
| `native` | Baseline. User asks in Thai, no hookglot. Claude answers Thai/mixed — the default experience. |
| `native_en` | User asks in English, no hookglot. Claude answers English. Isolates the pure language effect with no translation layer. |
| `hookglot` | Method 2. Claude is forced to answer English, then a hook translates to Thai via the configured provider. The product under test. |
| `hookglot_caveman` | hookglot + the *caveman* plugin (drops articles, filler, pleasantries). Tests English output combined with a terse style. |

Labels are free-form — any `label=path` works. These are just conventions.

---

## Methodology

1. **Run identical prompt sets across all modes** — same questions, same
   conditions, one transcript per mode.
2. **Drop turn 1** (default). Removes the system-prompt cache warm/cold noise.
   Use `--include-first` to keep it.
3. **Compare mode-to-mode, never against `/cost`.** Session overheads (haiku
   side-calls, turn 1) hit every mode equally, so a mode-vs-mode delta cancels
   them out; a script-vs-`/cost` comparison never reconciles.
4. **Auto-detect the model and use current pricing.** The script reads the model
   id from the transcript and maps it to live rates (e.g. Opus 4.8 = $5/$25 per M
   tokens). A stale price table once inflated cost ~3×.
5. **Use the language-neutral metric.** Compare **output tokens** and **cost**,
   not characters.
6. **Read patterns, not single spikes.** A one-off `cache_w` jump (such as the
   fixed turn-2 artifact that appears in *all* modes, including hook-free native)
   is a cache-miss or harness artifact, not a leak. Only a value that repeats
   every turn is a real signal.

---

## Running it

```bash
python benchmark.py \
  native=native.jsonl \
  native_en=native_en.jsonl \
  hookglot=hookglot.jsonl \
  hookglot_caveman=hookglot_caveman.jsonl \
  --baseline native \
  --hook-log ~/.hookglot/hook_debug.log   # optional: DeepSeek-side cost
```

Transcripts live at:

- Linux/macOS: `~/.claude/projects/<project>/<session>.jsonl`
- Windows: `%USERPROFILE%\.claude\projects\<project>\<session>.jsonl`

Useful flags:

- `--baseline <label>` — reference mode all others are compared against (default: first).
- `--include-first` — keep turn 1 in the aggregates (default: skipped).
- `--model <id>` — override the auto-detected pricing model.
- `--hook-log <path>` — add the DeepSeek translation-layer cost from `hook_debug.log`.

---

## Reading the output

Each mode prints token usage, a cost figure (for turns 2+), and a per-turn
**leak check** (`cache_w[N]` vs `output[N-1]`). The leak check is a heuristic:
treat a single large diff as "investigate", a per-turn repeating pattern as a
real leak. On recent Claude Code versions a fixed turn-2 spike appears in every
mode — that's a harness artifact, not a leak.

The final table shows `cost diff` and `char diff` versus the baseline. **Trust
`cost diff`; treat `char diff` as informational only** (it reflects language
density across modes, not content length).

---

## A reference result

A 5-prompt set of universal CS concept questions (turns 2–5, Opus 4.8):

| Mode | Out tok | Cost | cost diff |
|------|--------:|-----:|----------:|
| native | 7,667 | $0.2841 | base |
| native_en | 5,077 | $0.2091 | −26% |
| hookglot | 5,305 | $0.1894 | −33% |
| hookglot_caveman | 2,663 | $0.1165 | −59% |

**Savings scale with how much Thai the native baseline would naturally produce.**
A technical question that native already answers in English-heavy text → small
savings. A conversational/"explain simply" question that native answers in mostly
Thai → large savings.

---

## Caveats

- **Transcript schema is version-coupled.** Claude Code changes its `.jsonl`
  structure between releases. `benchmark.py` (and hookglot's hooks) parse that
  structure, so re-verify after any Claude Code update.
- **Exact `/cost` parity is impossible** by design (see trap #2). Compare modes,
  not absolute billing.
- **Prices change.** The pricing table is current as of mid-2026; verify before
  relying on the dollar figures.
