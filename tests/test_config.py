import os
import pytest
from stormcodai.config import Config

def test_rejects_credentials_in_base_url(monkeypatch):
    monkeypatch.setenv("STORMCODAI_BASE_URL","https://user:pass@example.com/v1")
    with pytest.raises(ValueError): Config.from_env()

def test_rejects_bad_timeout(monkeypatch):
    monkeypatch.setenv("STORMCODAI_REQUEST_TIMEOUT","2")
    with pytest.raises(ValueError): Config.from_env()
