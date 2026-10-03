from dataclasses import dataclass
import os
from urllib.parse import urlparse


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls) -> "Config":
        base_url = os.getenv("STORMCODAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("STORMCODAI_BASE_URL must be an absolute http(s) URL.")
        if parsed.username or parsed.password:
            raise ValueError("STORMCODAI_BASE_URL must not contain credentials.")
        return cls(
            api_key=os.getenv("STORMCODAI_API_KEY", ""),
            base_url=base_url,
            model=os.getenv("STORMCODAI_MODEL", "").strip(),
        )
