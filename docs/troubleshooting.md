# Troubleshooting

## Hooks not running

**Symptom**: Type Thai prompt but no translation happens.

**Check 1**: Verify hooks are installed
```bash
cat ~/.claude/settings.json
```
Should contain `"hooks"` section.

**Check 2**: Verify hookglot is installed and on PATH
```bash
which hookglot
python3 -m hookglot --version
```

**Check 3**: Run hook manually
```bash
echo '{"prompt": "ทดสอบ"}' | python3 -m hookglot.hooks.translate_input
```
Should output JSON.

**Fix**: Re-run `hookglot install` to regenerate settings.

---

## Translation is slow

**Cause**: Model is too large for your hardware (Ollama).

**Fix**: Use smaller model
```bash
ollama pull qwen2.5:3b
```
Then edit `~/.hookglot/config.yaml`:
```yaml
providers:
  ollama:
    model: qwen2.5:3b
```

Or use a cloud provider for faster response:
```bash
hookglot translator deepseek
```

---

## Translation timeout

**Symptom**: Hook runs but produces no output.

**Cause**: Translation took longer than the timeout (default 60s for input, 90s for output).

**Fix**: Edit `~/.claude/settings.json`, increase `timeout`:
```json
"timeout": 180
```

---

## Code blocks getting mangled

**Cause**: Translator model isn't preserving placeholders.

**Fix 1**: Use larger/better model
- Ollama: `qwen2.5:14b` instead of `qwen2.5:7b`
- Cloud: switch to `openai` or `anthropic` (best preservation)

**Fix 2**: Switch to Method 2 (no output translation, no risk)
```bash
hookglot switch 2
```

---

## "API key not found"

**Symptom**: Translation fails with auth error.

**Fix**:
```bash
hookglot set-key <provider>
```
Then verify:
```bash
cat ~/.hookglot/.env
```

---

## Quota exceeded mid-session

**Symptom**: 
```
⚠️  Translation failed
Provider : deepseek
Reason   : quota
```

**Fix**: Switch to another provider
```bash
hookglot translator ollama   # free fallback
```

The current response will remain in English (no retry, no auto-fallback by design).

---

## Claude responds in wrong language

**Method 1/3**: Claude responding in target language instead of English
- Master Prompt may not be loading
- Check `~/.claude/CLAUDE.md` exists and contains "Method N" overlay
- Re-run `hookglot install`

**Method 2**: Claude responding in English instead of target language
- Master Prompt overlay says respond in target language
- May happen if Claude reads code files and switches mode
- Explicitly ask: "ตอบเป็นภาษาไทยทุกครั้ง" (or your language)

---

## Ollama not starting

**Check**:
```bash
curl http://localhost:11434/api/tags
```

If empty/error:
```bash
ollama serve
```

If port conflict:
- Change port in `~/.hookglot/config.yaml`:
```yaml
providers:
  ollama:
    base_url: http://localhost:11435
```

---

## Settings.json corrupted

If Claude Code refuses to start due to bad settings.json:

```bash
mv ~/.claude/settings.json ~/.claude/settings.json.broken
hookglot install
```

A fresh settings.json will be generated.

---

## Hook breaks Claude Code agentic mode

If `claude` runs autonomous tasks (file editing, command execution) and translation
slows things down or causes errors:

**Fix**: Disable hooks for that session
```bash
HOOKGLOT_DISABLED=1 claude
```

Or uninstall:
```bash
hookglot uninstall
```

---

## Reset everything

```bash
hookglot uninstall
rm -rf ~/.hookglot
rm ~/.claude/CLAUDE.md      # if you only use it for hookglot
```

Then start fresh: `hookglot install`

---

## Windows-specific Issues

### "hookglot: command not found" after pip install

Windows installs scripts into `%APPDATA%\Python\Python3X\Scripts\` which may not
be in your PATH.

**Fix**: Add to PATH (PowerShell):
```powershell
$userBase = python -m site --user-base
$env:Path += ";$userBase\Scripts"
```

Or run directly:
```powershell
python -m hookglot install
python -m hookglot status
```

### Hooks fail silently on Windows

Check that the Python path in `~/.claude/settings.json` is correct:
```powershell
Get-Content $env:USERPROFILE\.claude\settings.json
```

The `command` field should contain the full path to your Python executable
(e.g., `"C:\\Python312\\python.exe" -m hookglot.hooks.translate_input`).

If it shows `python3` instead, re-run `hookglot install` to regenerate.

### Path with spaces

If your Python install is at a path with spaces (e.g., `C:\Program Files\Python\`),
hookglot handles quoting automatically. If you edit settings.json manually,
make sure the path is quoted:
```json
"command": "\"C:\\Program Files\\Python\\python.exe\" -m hookglot.hooks.translate_input"
```

### Reset on Windows

```powershell
hookglot uninstall
Remove-Item -Recurse -Force $env:USERPROFILE\.hookglot
Remove-Item $env:USERPROFILE\.claude\CLAUDE.md
hookglot install
```
