from dataclasses import dataclass
import os
from urllib.parse import urlparse


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str
    request_timeout: float = 60.0
    max_response_bytes: int = 4 * 1024 * 1024

    @classmethod
    def from_env(cls) -> "Config":
        base_url = os.getenv("STORMCODAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("STORMCODAI_BASE_URL must be an absolute http(s) URL.")
        if parsed.username or parsed.password or parsed.fragment:
            raise ValueError("STORMCODAI_BASE_URL must not contain credentials or fragments.")

        timeout_raw = os.getenv("STORMCODAI_REQUEST_TIMEOUT", "60").strip()
        response_limit_raw = os.getenv("STORMCODAI_MAX_RESPONSE_BYTES", str(4 * 1024 * 1024)).strip()
        try:
            timeout = float(timeout_raw)
            response_limit = int(response_limit_raw)
        except ValueError as exc:
            raise ValueError("Model timeout and response limit must be numeric.") from exc
        if not 5 <= timeout <= 300:
            raise ValueError("STORMCODAI_REQUEST_TIMEOUT must be between 5 and 300 seconds.")
        if not 64 * 1024 <= response_limit <= 32 * 1024 * 1024:
            raise ValueError("STORMCODAI_MAX_RESPONSE_BYTES is outside the allowed range.")

        return cls(
            api_key=os.getenv("STORMCODAI_API_KEY", ""),
            base_url=base_url,
            model=os.getenv("STORMCODAI_MODEL", "").strip(),
            request_timeout=timeout,
            max_response_bytes=response_limit,
        )
