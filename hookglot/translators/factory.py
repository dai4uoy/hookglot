"""Factory for creating translator instances by provider name."""
from hookglot.translators.base import BaseTranslator
from hookglot.translators.ollama import OllamaTranslator
from hookglot.translators.openai_compatible import OpenAICompatibleTranslator
from hookglot.translators.anthropic import AnthropicTranslator
from hookglot.translators.google import GoogleTranslator


# Providers that use OpenAI-compatible chat completions API
OPENAI_COMPATIBLE = {"openai", "deepseek", "moonshot", "zhipu", "alibaba", "nvidia"}


def get_translator(provider_name: str, provider_config: dict) -> BaseTranslator:
    """Create a translator instance for the given provider.

    Args:
        provider_name: Name of provider (ollama, openai, deepseek, etc.)
        provider_config: Provider config dict from config.yaml

    Returns:
        Configured translator instance

    Raises:
        ValueError: If provider is not supported
    """
    if provider_name == "ollama":
        return OllamaTranslator(provider_config)
    elif provider_name == "anthropic":
        return AnthropicTranslator(provider_config)
    elif provider_name == "google":
        return GoogleTranslator(provider_config)
    elif provider_name in OPENAI_COMPATIBLE:
        return OpenAICompatibleTranslator(provider_config, provider_name=provider_name)
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Supported: ollama, openai, anthropic, google, deepseek, "
            f"alibaba, moonshot, zhipu, nvidia"
        )


SUPPORTED_PROVIDERS = ["ollama", "openai", "anthropic", "google",
                       "deepseek", "alibaba", "moonshot", "zhipu", "nvidia"]
