from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            api_key=os.getenv("STORMCODAI_API_KEY", ""),
            base_url=os.getenv("STORMCODAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            model=os.getenv("STORMCODAI_MODEL", ""),
        )
