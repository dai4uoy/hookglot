"""Ollama (local LLM) translator."""
import json
import urllib.request
import urllib.error

from hookglot.translators.base import BaseTranslator, TranslationError


class OllamaTranslator(BaseTranslator):
    name = "ollama"

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434").rstrip("/")
        self.model = config.get("model", "qwen2.5:7b")
        self.timeout = config.get("timeout", 60)

    def health_check(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _call_api(self, system_prompt: str, user_text: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 4096,
            },
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read())
                return result["message"]["content"].strip()
        except urllib.error.URLError as e:
            raise TranslationError(self.name, "network", f"Cannot reach Ollama: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise TranslationError(self.name, "unknown", f"Invalid response: {e}")
        except Exception as e:
            raise TranslationError(self.name, "unknown", str(e))
