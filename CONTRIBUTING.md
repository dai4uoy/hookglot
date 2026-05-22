# Contributing to hookglot

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/yourusername/hookglot.git
cd hookglot
pip install -e ".[dev]"
```

## Areas Where Help Is Welcome

### 🌍 More Language Support

Currently supports 8 Asian languages. To add another:

1. Add entry to `hookglot/language.py` `LANGUAGES` dict
2. Add test sample in `hookglot/cli/commands.py` `cmd_test()` function's `test_samples`
3. Test translation with your provider
4. Submit PR

### 🤖 More Translator Providers

To add a new provider:

1. If it's OpenAI-compatible: add config to `hookglot/config.py` `DEFAULT_CONFIG["providers"]`
   and register in `hookglot/translators/factory.py` `OPENAI_COMPATIBLE` set
2. Otherwise: create new file `hookglot/translators/<name>.py` extending `BaseTranslator`
3. Add to `factory.py` `get_translator()` function
4. Update `SUPPORTED_PROVIDERS` list
5. Document in `docs/providers.md`

### 🛡️ Better Format Preservation

Improve `hookglot/format_preservation.py`:
- Add new patterns to `PRESERVE_PATTERNS`
- Improve placeholder restoration logic
- Add tests for edge cases

### 🐛 Bug Fixes

Found a bug? Open an issue with:
- Your config (`hookglot status` output)
- Steps to reproduce
- Expected vs actual behavior
- Hook stderr output if available

### 📝 Documentation

- Translate docs to other languages
- Add usage examples
- Improve troubleshooting guide

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
ruff check hookglot/
ruff format hookglot/
```

### Testing Hooks Manually

```bash
# Test input hook
echo '{"prompt": "ทดสอบ Pass-the-Hash"}' | python3 -m hookglot.hooks.translate_input

# Test output hook (need a real transcript)
echo '{"transcript_path": "/path/to/transcript.jsonl"}' | python3 -m hookglot.hooks.translate_output
```

### Testing Translators

```bash
hookglot test
```

## Pull Request Process

1. Fork & branch (`git checkout -b feature/my-feature`)
2. Make your changes
3. Add tests if applicable
4. Run linter (`ruff check hookglot/`)
5. Update docs
6. Submit PR with clear description

## Code of Conduct

Be kind. Be respectful. Help others.
