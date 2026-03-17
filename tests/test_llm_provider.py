from __future__ import annotations

from src.core.llm_provider import ProxyClient, create_llm_client


# ---------------------------------------------------------------------------
# Factory returns ProxyClient with correct defaults
# ---------------------------------------------------------------------------


def test_factory_returns_proxy_client_with_default_model() -> None:
    client = create_llm_client()
    assert isinstance(client, ProxyClient)
    assert client.provider_name == "anthropic"
    assert client.model_id == "claude-sonnet-4-6"


def test_factory_returns_proxy_client_with_custom_model() -> None:
    client = create_llm_client("claude-opus-4-6")
    assert isinstance(client, ProxyClient)
    assert client.provider_name == "anthropic"
    assert client.model_id == "claude-opus-4-6"
