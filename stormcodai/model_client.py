import json
import urllib.request
from .config import Config

class ModelClient:
    def __init__(self, config: Config):
        self.config = config

    def chat(self, system: str, user: str) -> str:
        if not self.config.api_key or not self.config.model:
            raise RuntimeError("Set STORMCODAI_API_KEY and STORMCODAI_MODEL first.")
        payload = json.dumps({
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }).encode()
        req = urllib.request.Request(
            self.config.base_url + "/chat/completions",
            data=payload,
            headers={
                "Authorization": "Bearer " + self.config.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode())
        return data["choices"][0]["message"]["content"]
