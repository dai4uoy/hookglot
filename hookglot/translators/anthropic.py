"""Anthropic Claude (Haiku) translator."""
import json
import os
import urllib.request
import urllib.error

from hookglot.translators.base import BaseTranslator, TranslationError


class AnthropicTranslator(BaseTranslator):
    name = "anthropic"

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.anthropic.com/v1").rstrip("/")
        self.model = config.get("model", "claude-haiku-4-5")
        self.api_key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
        self.timeout = config.get("timeout", 60)

    def _get_api_key(self) -> str:
        key = os.environ.get(self.api_key_env, "")
        if not key:
            raise TranslationError(
                self.name,
                "auth",
                f"API key not found in {self.api_key_env}",
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
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.1,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read())
                # Response format: {"content": [{"type": "text", "text": "..."}]}
                content_blocks = result.get("content", [])
                texts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
                return "\n".join(texts).strip()
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
                raise TranslationError(self.name, "quota", f"Rate limit: {msg}")
            elif 500 <= status < 600:
                raise TranslationError(self.name, "server", f"Anthropic error {status}: {msg}")
            else:
                raise TranslationError(self.name, "unknown", f"HTTP {status}: {msg}")
        except urllib.error.URLError as e:
            raise TranslationError(self.name, "network", f"Network error: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise TranslationError(self.name, "unknown", f"Invalid response: {e}")
        except Exception as e:
            raise TranslationError(self.name, "unknown", str(e))
