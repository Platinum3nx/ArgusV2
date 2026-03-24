from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from src.core.llm_provider import ConfigurationError, ProxyClient, create_llm_client


def test_factory_returns_proxy_client_with_default_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARGUS_PROXY_TOKEN", "token")
    client = create_llm_client()
    assert isinstance(client, ProxyClient)
    assert client.provider_name == "anthropic"
    assert client.model_id == "claude-sonnet-4-6"
    assert client.connect_timeout_seconds == 5.0
    assert client.read_timeout_seconds == 45.0


def test_factory_returns_proxy_client_with_custom_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARGUS_PROXY_TOKEN", "token")
    client = create_llm_client("anthropic", "claude-opus-4-6")
    assert isinstance(client, ProxyClient)
    assert client.provider_name == "anthropic"
    assert client.model_id == "claude-opus-4-6"


def test_factory_reads_timeout_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARGUS_PROXY_TOKEN", "token")
    monkeypatch.setenv("ARGUS_PROXY_CONNECT_TIMEOUT_SECONDS", "7")
    monkeypatch.setenv("ARGUS_PROXY_READ_TIMEOUT_SECONDS", "19.5")

    client = create_llm_client()
    assert isinstance(client, ProxyClient)
    assert client.connect_timeout_seconds == 7.0
    assert client.read_timeout_seconds == 19.5


def test_factory_ignores_invalid_timeout_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARGUS_PROXY_TOKEN", "token")
    monkeypatch.setenv("ARGUS_PROXY_CONNECT_TIMEOUT_SECONDS", "bogus")
    monkeypatch.setenv("ARGUS_PROXY_READ_TIMEOUT_SECONDS", "-1")

    client = create_llm_client()
    assert isinstance(client, ProxyClient)
    assert client.connect_timeout_seconds == 5.0
    assert client.read_timeout_seconds == 45.0


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
        headers: dict[str, str] = {}

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


def test_proxy_client_uses_connect_and_read_timeouts(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class GoodResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"text": "ok"}

    def fake_post(*args, **kwargs):
        captured["timeout"] = kwargs["timeout"]
        return GoodResp()

    monkeypatch.setattr("src.core.llm_provider.requests.post", fake_post)
    c = ProxyClient(
        model="claude-sonnet-4-6",
        proxy_url="http://proxy",
        proxy_token="tok",
        connect_timeout_seconds=3,
        read_timeout_seconds=11,
    )

    assert c.generate("hello") == "ok"
    assert captured["timeout"] == (3.0, 11.0)


def test_proxy_client_raises_on_invalid_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    class BadResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"unexpected": "shape"}

    monkeypatch.setattr("src.core.llm_provider.requests.post", lambda *a, **k: BadResp())
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda *_: None)

    c = ProxyClient(model="claude-sonnet-4-6", proxy_url="http://proxy", proxy_token="tok")
    with pytest.raises(ValueError, match="missing 'text' field"):
        c.generate("hello")


# ---------------------------------------------------------------------------
# P0.4 — Retry-After + jitter tests
# ---------------------------------------------------------------------------


def test_retry_after_header_honoured(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock 429 with Retry-After: 5 header. Assert sleep called with value near 5 (within jitter bounds 3.75-6.25)."""

    class Resp429:
        status_code = 429
        headers = {"Retry-After": "5"}

        def raise_for_status(self) -> None:
            raise requests.HTTPError(response=self)

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
        if calls["n"] < 2:
            return Resp429()
        return GoodResp()

    sleep_values: list[float] = []
    monkeypatch.setattr("src.core.llm_provider.requests.post", fake_post)
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda v: sleep_values.append(v))

    c = ProxyClient(model="m", proxy_url="http://proxy", proxy_token="tok")
    assert c.generate("hello") == "ok"
    assert len(sleep_values) == 1
    # 5 +/- 25% jitter → [3.75, 6.25]
    assert 3.75 <= sleep_values[0] <= 6.25


def test_retry_after_clamped_to_60(monkeypatch: pytest.MonkeyPatch) -> None:
    """Retry-After values above 60 are clamped to 60 (plus jitter)."""

    class Resp429:
        status_code = 429
        headers = {"Retry-After": "120"}

        def raise_for_status(self) -> None:
            raise requests.HTTPError(response=self)

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
        if calls["n"] < 2:
            return Resp429()
        return GoodResp()

    sleep_values: list[float] = []
    monkeypatch.setattr("src.core.llm_provider.requests.post", fake_post)
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda v: sleep_values.append(v))

    c = ProxyClient(model="m", proxy_url="http://proxy", proxy_token="tok")
    assert c.generate("hello") == "ok"
    # clamped to 60 +/- 25% jitter → [45, 75]
    assert 45 <= sleep_values[0] <= 75


# ---------------------------------------------------------------------------
# A0.2 / P1.3 — ValueError retry and schema validation tests
# ---------------------------------------------------------------------------


def test_invalid_payload_retried_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock 200 with {'wrong_key': 'value'} on first call, valid on second. Assert retry happens."""

    class BadResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"wrong_key": "value"}

    class GoodResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"text": "success"}

    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 2:
            return BadResp()
        return GoodResp()

    monkeypatch.setattr("src.core.llm_provider.requests.post", fake_post)
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda *_: None)

    c = ProxyClient(model="m", proxy_url="http://proxy", proxy_token="tok")
    assert c.generate("hello") == "success"
    assert calls["n"] == 2


def test_non_json_body_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock 200 with non-JSON body. Assert retry happens and eventually succeeds."""

    class NonJsonResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            raise ValueError("No JSON object could be decoded")

    class GoodResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"text": "ok"}

    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 2:
            return NonJsonResp()
        return GoodResp()

    monkeypatch.setattr("src.core.llm_provider.requests.post", fake_post)
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda *_: None)

    c = ProxyClient(model="m", proxy_url="http://proxy", proxy_token="tok")
    assert c.generate("hello") == "ok"
    assert calls["n"] == 2


def test_empty_text_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock response with {'text': ''} — assert ValueError raised after retries exhausted."""

    class EmptyTextResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"text": ""}

    monkeypatch.setattr("src.core.llm_provider.requests.post", lambda *a, **k: EmptyTextResp())
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda *_: None)

    c = ProxyClient(model="m", proxy_url="http://proxy", proxy_token="tok")
    with pytest.raises(ValueError, match="empty or non-string"):
        c.generate("hello")


def test_list_payload_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock response with [1, 2, 3] (list not dict) — assert ValueError raised after retries exhausted."""

    class ListResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return [1, 2, 3]

    monkeypatch.setattr("src.core.llm_provider.requests.post", lambda *a, **k: ListResp())
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda *_: None)

    c = ProxyClient(model="m", proxy_url="http://proxy", proxy_token="tok")
    with pytest.raises(ValueError, match="missing 'text' field"):
        c.generate("hello")


def test_retry_exhaustion_does_not_sleep_after_final_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    class Resp429:
        status_code = 429
        headers: dict[str, str] = {}

        def json(self):
            return {}

    sleep_values: list[float] = []
    monkeypatch.setattr("src.core.llm_provider.requests.post", lambda *a, **k: Resp429())
    monkeypatch.setattr("src.core.llm_provider.time.sleep", lambda v: sleep_values.append(v))
    monkeypatch.setattr("src.core.llm_provider.random.random", lambda: 0.5)

    c = ProxyClient(model="m", proxy_url="http://proxy", proxy_token="tok")
    with pytest.raises(requests.HTTPError):
        c.generate("hello")

    assert len(sleep_values) == 2
