from __future__ import annotations

import pytest

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
