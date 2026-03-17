from __future__ import annotations

import pytest
import requests

from src.core.llm_provider import ConfigurationError, ProxyClient, create_llm_client


def test_factory_returns_proxy_client_with_default_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARGUS_PROXY_TOKEN", "token")
    client = create_llm_client()
    assert isinstance(client, ProxyClient)
    assert client.provider_name == "anthropic"
    assert client.model_id == "claude-sonnet-4-6"


def test_factory_returns_proxy_client_with_custom_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARGUS_PROXY_TOKEN", "token")
    client = create_llm_client("anthropic", "claude-opus-4-6")
    assert isinstance(client, ProxyClient)
    assert client.provider_name == "anthropic"
    assert client.model_id == "claude-opus-4-6"


def test_factory_rejects_non_anthropic_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARGUS_PROXY_TOKEN", "token")
    with pytest.raises(ConfigurationError, match="not supported in hosted mode"):
        create_llm_client("gemini")


def test_factory_requires_proxy_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARGUS_PROXY_TOKEN", raising=False)
    with pytest.raises(ConfigurationError, match="ARGUS_PROXY_TOKEN is not set"):
        create_llm_client("anthropic")


def test_proxy_client_retries_and_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResp:
        status_code = 503

        def raise_for_status(self) -> None:
            raise requests.HTTPError("503")

        def json(self):
            return {}

    class GoodResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"text": "ok"}

    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            return FakeResp()
        return GoodResp()

    monkeypatch.setattr("src.core.llm_provider.requests.post", fake_post)
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda *_: None)

    c = ProxyClient(model="claude-sonnet-4-6", proxy_url="http://proxy", proxy_token="tok")
    assert c.generate("hello") == "ok"
    assert calls["n"] == 3


def test_proxy_client_raises_on_invalid_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    class BadResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"unexpected": "shape"}

    monkeypatch.setattr("src.core.llm_provider.requests.post", lambda *a, **k: BadResp())

    c = ProxyClient(model="claude-sonnet-4-6", proxy_url="http://proxy", proxy_token="tok")
    with pytest.raises(ValueError, match="invalid payload"):
        c.generate("hello")
