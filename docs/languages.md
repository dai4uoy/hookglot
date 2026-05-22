# Supported Languages

hookglot currently supports 8 Asian languages.

| Code | Language | Native | Detection |
|------|----------|--------|-----------|
| `th` | Thai | ภาษาไทย | Unicode (U+0E00–U+0E7F) |
| `ja` | Japanese | 日本語 | Unicode (Hiragana, Katakana, Kanji) |
| `zh-CN` | Chinese (Simplified) | 简体中文 | Unicode (CJK) |
| `zh-TW` | Chinese (Traditional) | 繁體中文 | Unicode (CJK) |
| `ko` | Korean | 한국어 | Unicode (Hangul) |
| `vi` | Vietnamese | Tiếng Việt | User config (Latin) |
| `id` | Indonesian | Bahasa Indonesia | User config (Latin) |
| `ms` | Malay | Bahasa Melayu | User config (Latin) |

## Switching Languages

```bash
hookglot lang th        # Thai
hookglot lang ja        # Japanese
hookglot lang zh-CN     # Chinese Simplified
hookglot lang zh-TW     # Chinese Traditional
hookglot lang ko        # Korean
hookglot lang vi        # Vietnamese
hookglot lang id        # Indonesian
hookglot lang ms        # Malay
```

After switching, the Master Prompt at `~/.claude/CLAUDE.md` is regenerated with
language-specific instructions.

## Language Detection

For non-Latin scripts (Thai, Japanese, Chinese, Korean), hookglot uses Unicode
character ranges to detect when a prompt is in the target language. If your
prompt is pure ASCII, hooks skip translation.

For Latin-based languages (Vietnamese, Indonesian, Malay), Unicode detection
isn't reliable. The hook assumes any non-empty prompt is in your configured
target language.

## Adding More Languages

To add a new language, edit `hookglot/language.py`:

```python
LANGUAGES["es"] = Language(
    code="es",
    english_name="Spanish",
    native_name="Español",
    unicode_ranges=[],
    uses_latin=True,
)
```

Then submit a pull request!

## Translator Quality by Language

Translation quality depends on the provider's training data:

| Language | Ollama (Qwen) | OpenAI | Anthropic | DeepSeek | Google |
|----------|---------------|--------|-----------|----------|--------|
| Thai | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Japanese | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Chinese (S) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Chinese (T) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Korean | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Vietnamese | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Indonesian | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Malay | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

Test your specific use case with `hookglot test` to verify quality.
