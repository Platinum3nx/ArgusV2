from __future__ import annotations

import sys
import types

import pytest

from src.core.llm_provider import ConfigurationError, create_llm_client


def _fake_anthropic_module() -> types.ModuleType:
    mod = types.ModuleType("anthropic")

    class _FakeAnthropicClass:
        def __init__(self, api_key: str) -> None:
            pass

    mod.Anthropic = _FakeAnthropicClass  # type: ignore[attr-defined]
    return mod


def _fake_genai_module() -> types.ModuleType:
    google_mod = types.ModuleType("google")
    genai_mod = types.ModuleType("google.genai")

    class _FakeGenaiClient:
        def __init__(self, api_key: str) -> None:
            pass

    genai_mod.Client = _FakeGenaiClient  # type: ignore[attr-defined]
    google_mod.genai = genai_mod  # type: ignore[attr-defined]
    return google_mod, genai_mod


# ---------------------------------------------------------------------------
# Fail-closed: missing / empty API key
# ---------------------------------------------------------------------------


def test_factory_raises_on_missing_anthropic_key(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY"):
        create_llm_client("anthropic")


def test_factory_raises_on_empty_anthropic_key(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
    with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY"):
        create_llm_client("anthropic")


def test_factory_raises_on_missing_gemini_key(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
        create_llm_client("gemini")


def test_factory_raises_on_empty_gemini_key(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "   ")
    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
        create_llm_client("gemini")


def test_factory_raises_on_unknown_provider() -> None:
    with pytest.raises(ConfigurationError, match="Unknown"):
        create_llm_client("openai")


# ---------------------------------------------------------------------------
# Fail-closed: missing SDK
# ---------------------------------------------------------------------------


def test_factory_raises_when_anthropic_sdk_missing(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "anthropic", None)  # type: ignore[arg-type]
    with pytest.raises(ConfigurationError, match="anthropic SDK"):
        create_llm_client("anthropic")


# ---------------------------------------------------------------------------
# Success path: correct provider_name and model_id
# ---------------------------------------------------------------------------


def test_factory_returns_anthropic_client_with_default_model(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "anthropic", _fake_anthropic_module())
    client = create_llm_client("anthropic")
    assert client.provider_name == "anthropic"
    assert client.model_id == "claude-sonnet-4-6"


def test_factory_returns_anthropic_client_with_custom_model(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "anthropic", _fake_anthropic_module())
    client = create_llm_client("anthropic", "claude-opus-4-6")
    assert client.provider_name == "anthropic"
    assert client.model_id == "claude-opus-4-6"
