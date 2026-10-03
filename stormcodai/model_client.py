from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .config import Config


@dataclass(frozen=True)
class ModelResult:
    content: str
    model: str
    usage: dict[str, Any] | None = None


class ModelClient:
    """Small, bounded OpenAI-compatible client using only the Python stdlib."""

    def __init__(self, config: Config):
        self.config = config

    def chat(self, system: str, user: str) -> str:
        return self.chat_result(system, user).content

    def chat_result(self, system: str, user: str) -> ModelResult:
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
                "User-Agent": "StormCodAI/0.1",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.config.request_timeout) as response:
                raw = response.read(self.config.max_response_bytes + 1)
        except urllib.error.HTTPError as exc:
            # Never return the provider body: it may contain secrets or internal data.
            raise RuntimeError(f"Model API returned HTTP {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError("Could not reach the model service.") from exc
        except TimeoutError as exc:
            raise RuntimeError("Model API request timed out.") from exc

        if len(raw) > self.config.max_response_bytes:
            raise RuntimeError("Model API response exceeded the configured limit.")

        try:
            data = json.loads(raw.decode("utf-8"))
            choice = data["choices"][0]
            message = choice["message"]
            content = message["content"]
            model = data.get("model") or self.config.model
            usage = data.get("usage")
        except (KeyError, IndexError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Model API returned an unexpected response format.") from exc

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Model API returned an empty response.")
        if not isinstance(model, str):
            model = self.config.model
        if usage is not None and not isinstance(usage, dict):
            usage = None
        return ModelResult(content=content, model=model, usage=usage)
