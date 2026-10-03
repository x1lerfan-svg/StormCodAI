import json
import urllib.error
import urllib.request

from .config import Config


class ModelClient:
    """Small OpenAI-compatible chat-completions client using only stdlib."""

    def __init__(self, config: Config):
        self.config = config

    def chat(self, system: str, user: str) -> str:
        if not self.config.api_key:
            raise RuntimeError("STORMCODAI_API_KEY is not configured.")
        if not self.config.model:
            raise RuntimeError("STORMCODAI_MODEL is not configured.")

        payload = json.dumps({
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }).encode("utf-8")

        request = urllib.request.Request(
            f"{self.config.base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            raise RuntimeError(f"Model API returned HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach model API: {exc.reason}") from exc
        except TimeoutError as exc:
            raise RuntimeError("Model API request timed out.") from exc

        try:
            data = json.loads(raw)
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Model API returned an unexpected response format.") from exc

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Model API returned an empty response.")
        return content
