"""Abstract base translator interface."""
from abc import ABC, abstractmethod

from hookglot.format_preservation import preserve, get_translator_instruction
from hookglot.language import LANGUAGES


class TranslationError(Exception):
    """Translation operation failed.

    Attributes:
        provider: Name of the failing provider
        reason: Short reason category (quota, network, auth, timeout, unknown)
        message: Human-readable error message
    """

    def __init__(self, provider: str, reason: str, message: str):
        self.provider = provider
        self.reason = reason
        self.message = message
        super().__init__(f"[{provider}] {reason}: {message}")


class BaseTranslator(ABC):
    """Abstract translator with format preservation built in.

    Subclasses only need to implement `_call_api()`.
    """

    name: str = "base"  # override in subclass

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def _call_api(self, system_prompt: str, user_text: str) -> str:
        """Make actual API call. Should raise TranslationError on failure."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Check if provider is reachable and ready."""
        ...

    def translate(self, text: str, source_lang_code: str, target_lang_code: str) -> str:
        """Translate text with format preservation.

        Returns translated text with all preserved elements restored.
        Raises TranslationError on failure.
        """
        if not text.strip():
            return text

        # Layer 1+2: Extract preservable elements
        doc = preserve(text)

        # Layer 3: Strict prompt
        source_lang = LANGUAGES[source_lang_code].english_name if source_lang_code in LANGUAGES else source_lang_code
        target_lang = LANGUAGES[target_lang_code].english_name if target_lang_code in LANGUAGES else target_lang_code
        system_prompt = get_translator_instruction(source_lang, target_lang)

        # Call provider API
        translated = self._call_api(system_prompt, doc.text)

        # Restore preserved elements
        return doc.restore(translated)
