"""Google Gemini translator."""
import json
import os
import urllib.request
import urllib.error
import urllib.parse

from hookglot.translators.base import BaseTranslator, TranslationError


class GoogleTranslator(BaseTranslator):
    name = "google"

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get(
            "base_url", "https://generativelanguage.googleapis.com/v1beta"
        ).rstrip("/")
        self.model = config.get("model", "gemini-2.0-flash")
        self.api_key_env = config.get("api_key_env", "GOOGLE_API_KEY")
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

        # Gemini API format
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_text}],
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}],
            },
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 4096,
            },
        }

        data = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/models/{self.model}:generateContent?key={urllib.parse.quote(api_key)}"
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read())
                # Response: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
                candidates = result.get("candidates", [])
                if not candidates:
                    raise TranslationError(self.name, "unknown", "Empty response")
                parts = candidates[0].get("content", {}).get("parts", [])
                texts = [p.get("text", "") for p in parts]
                return "\n".join(texts).strip()
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                body = json.loads(e.read())
                msg = body.get("error", {}).get("message", str(e))
            except Exception:
                msg = str(e)

            if status == 400 and "API key" in msg:
                raise TranslationError(self.name, "auth", f"Invalid API key: {msg}")
            elif status in (401, 403):
                raise TranslationError(self.name, "auth", f"Auth error: {msg}")
            elif status == 429:
                raise TranslationError(self.name, "quota", f"Rate limit/quota: {msg}")
            elif 500 <= status < 600:
                raise TranslationError(self.name, "server", f"Google error {status}: {msg}")
            else:
                raise TranslationError(self.name, "unknown", f"HTTP {status}: {msg}")
        except urllib.error.URLError as e:
            raise TranslationError(self.name, "network", f"Network error: {e}")
        except (KeyError, json.JSONDecodeError, IndexError) as e:
            raise TranslationError(self.name, "unknown", f"Invalid response: {e}")
        except Exception as e:
            raise TranslationError(self.name, "unknown", str(e))
