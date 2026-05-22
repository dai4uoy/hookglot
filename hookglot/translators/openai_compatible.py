"""OpenAI-compatible translator.

Used by: OpenAI, DeepSeek, Moonshot, Zhipu, Alibaba (DashScope), NVIDIA
All these providers expose an OpenAI-format chat completion API.
"""
import json
import os
import urllib.request
import urllib.error

from hookglot.translators.base import BaseTranslator, TranslationError


class OpenAICompatibleTranslator(BaseTranslator):
    """Translator for any provider with OpenAI-compatible /v1/chat/completions."""

    def __init__(self, config: dict, provider_name: str = "openai"):
        super().__init__(config)
        self.name = provider_name
        self.base_url = config["base_url"].rstrip("/")
        self.model = config["model"]
        self.api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
        self.timeout = config.get("timeout", 60)

    def _get_api_key(self) -> str:
        key = os.environ.get(self.api_key_env, "")
        if not key:
            raise TranslationError(
                self.name,
                "auth",
                f"API key not found in environment variable {self.api_key_env}. "
                f"Run: hookglot set-key {self.name}",
            )
        return key

    def health_check(self) -> bool:
        try:
            self._get_api_key()
            return True
        except TranslationError:
            return False

    def _call_api(self, system_prompt: str, user_text: str) -> str:
        api_key = self._get_api_key()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.1,
            "max_tokens": 4096,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                body = json.loads(e.read())
                msg = body.get("error", {}).get("message", str(e))
            except Exception:
                msg = str(e)

            if status == 401:
                raise TranslationError(self.name, "auth", f"Invalid API key: {msg}")
            elif status == 429:
                raise TranslationError(self.name, "quota", f"Rate limit/quota exceeded: {msg}")
            elif status == 402:
                raise TranslationError(self.name, "quota", f"Payment required: {msg}")
            elif 500 <= status < 600:
                raise TranslationError(self.name, "server", f"Provider error {status}: {msg}")
            else:
                raise TranslationError(self.name, "unknown", f"HTTP {status}: {msg}")
        except urllib.error.URLError as e:
            raise TranslationError(self.name, "network", f"Network error: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise TranslationError(self.name, "unknown", f"Invalid response: {e}")
        except Exception as e:
            raise TranslationError(self.name, "unknown", str(e))
