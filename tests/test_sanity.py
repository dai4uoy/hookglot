"""Quick sanity test of imports and basic functionality."""
import sys
import os

# Add parent to path so we can import without installing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Just verify everything imports cleanly."""
    from hookglot import __version__
    from hookglot.config import load_config, DEFAULT_CONFIG
    from hookglot.language import LANGUAGES, get_language, has_target_language_chars
    from hookglot.format_preservation import preserve, get_translator_instruction
    from hookglot.translators.factory import get_translator, SUPPORTED_PROVIDERS
    from hookglot.translators.base import BaseTranslator, TranslationError

    assert __version__ == "1.2.0"
    assert "th" in LANGUAGES
    assert "ja" in LANGUAGES
    assert "ollama" in SUPPORTED_PROVIDERS
    assert "deepseek" in SUPPORTED_PROVIDERS
    assert len(SUPPORTED_PROVIDERS) == 9


def test_language_detection():
    from hookglot.language import has_target_language_chars
    assert has_target_language_chars("สวัสดี Pass-the-Hash", "th") is True
    assert has_target_language_chars("Hello world", "th") is False
    assert has_target_language_chars("こんにちは", "ja") is True
    assert has_target_language_chars("你好世界", "zh-CN") is True


def test_config_defaults():
    from hookglot.config import DEFAULT_CONFIG
    assert DEFAULT_CONFIG["language"] == "th"
    assert DEFAULT_CONFIG["method"] == 1
    assert DEFAULT_CONFIG["translator"] == "ollama"
    assert "deepseek" in DEFAULT_CONFIG["providers"]
    assert "moonshot" in DEFAULT_CONFIG["providers"]


def test_factory_creates_translators():
    from hookglot.translators.factory import get_translator, SUPPORTED_PROVIDERS
    from hookglot.config import DEFAULT_CONFIG

    for provider in SUPPORTED_PROVIDERS:
        cfg = DEFAULT_CONFIG["providers"][provider]
        translator = get_translator(provider, cfg)
        assert translator is not None
        assert translator.name == provider


if __name__ == "__main__":
    test_imports()
    print("✅ Imports OK")
    test_language_detection()
    print("✅ Language detection OK")
    test_config_defaults()
    print("✅ Config defaults OK")
    test_factory_creates_translators()
    print("✅ All translators instantiate")
    print("\n🎉 All tests passed!")
