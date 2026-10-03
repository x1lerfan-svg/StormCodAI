import os
import pytest
from stormcodai.config import Config

def test_rejects_credentials_in_base_url(monkeypatch):
    monkeypatch.setenv("STORMCODAI_BASE_URL","https://user:pass@example.com/v1")
    with pytest.raises(ValueError): Config.from_env()

def test_rejects_public_http(monkeypatch):
    monkeypatch.setenv("STORMCODAI_BASE_URL", "http://example.com/v1")
    with pytest.raises(ValueError):
        Config.from_env()


def test_allows_loopback_http(monkeypatch):
    monkeypatch.setenv("STORMCODAI_BASE_URL", "http://127.0.0.1:11434/v1")
    assert Config.from_env().base_url == "http://127.0.0.1:11434/v1"


def test_rejects_bad_timeout(monkeypatch):
    monkeypatch.setenv("STORMCODAI_REQUEST_TIMEOUT","2")
    with pytest.raises(ValueError): Config.from_env()
