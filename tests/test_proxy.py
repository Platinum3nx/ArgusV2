"""Tests for proxy/main.py — request guardrails, IP resolution, and correlation IDs."""

from __future__ import annotations

import os
import uuid

import pytest
from unittest.mock import patch, MagicMock

# Set env vars BEFORE importing proxy.main so module-level code picks them up.
os.environ.setdefault("ARGUS_PROXY_TOKEN", "test-token")
os.environ.setdefault("ANTHROPIC_API_KEY", "fake-key-for-tests")

from fastapi.testclient import TestClient
from proxy.main import app, TOKEN_CONFIG, MAX_PROMPT_CHARS, MAX_TOKENS_CEILING


@pytest.fixture(autouse=True)
def _ensure_token_config():
    """Make sure TOKEN_CONFIG has our test token for every test."""
    TOKEN_CONFIG.setdefault("test-token", {"name": "test", "daily_limit": 500})
    yield


@pytest.fixture()
def tc():
    return TestClient(app)


# Helpers ----------------------------------------------------------------

AUTH_HEADER = {"x-argus-token": "test-token"}


def _mock_anthropic_response(text: str = "hello") -> MagicMock:
    """Return a mock that looks like an Anthropic messages.create response."""
    content_block = MagicMock()
    content_block.text = text
    resp = MagicMock()
    resp.content = [content_block]
    return resp


# Tests ------------------------------------------------------------------


class TestOversizedPrompt:
    """P0.3 — oversized prompt returns 413."""

    def test_prompt_too_large(self, tc: TestClient):
        huge_prompt = "x" * (MAX_PROMPT_CHARS + 1)
        resp = tc.post(
            "/generate",
            json={"prompt": huge_prompt, "model": "claude-sonnet-4-6"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 413
        assert "Prompt exceeds maximum size" in resp.json()["detail"]


class TestMaxTokensClamped:
    """P0.3 — max_tokens is clamped to MAX_TOKENS_CEILING."""

    @patch("proxy.main.client")
    def test_max_tokens_clamped(self, mock_client, tc: TestClient):
        mock_client.messages.create.return_value = _mock_anthropic_response("ok")

        tc.post(
            "/generate",
            json={
                "prompt": "hi",
                "model": "claude-sonnet-4-6",
                "max_tokens": 999999,
            },
            headers=AUTH_HEADER,
        )
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs is not None
        assert call_kwargs.kwargs["max_tokens"] <= MAX_TOKENS_CEILING

    @patch("proxy.main.client")
    def test_max_tokens_must_be_positive(self, mock_client, tc: TestClient):
        resp = tc.post(
            "/generate",
            json={
                "prompt": "hi",
                "model": "claude-sonnet-4-6",
                "max_tokens": -5,
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 422
        mock_client.messages.create.assert_not_called()


class TestDisallowedModel:
    """P0.3 — disallowed model returns 422."""

    def test_disallowed_model(self, tc: TestClient):
        resp = tc.post(
            "/generate",
            json={"prompt": "hi", "model": "gpt-4-turbo"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 422
        assert "not allowed" in resp.json()["detail"]


class TestXForwardedFor:
    """A1.4 — forwarded headers are only used when explicitly trusted."""

    @patch("proxy.main.client")
    def test_forwarded_for_used_when_trusted(self, mock_client, tc: TestClient, monkeypatch):
        mock_client.messages.create.return_value = _mock_anthropic_response("ok")
        monkeypatch.setenv("ARGUS_TRUST_PROXY_HEADERS", "true")

        headers = {**AUTH_HEADER, "X-Forwarded-For": "203.0.113.50, 10.0.0.1"}
        resp = tc.post(
            "/generate",
            json={"prompt": "hi", "model": "claude-sonnet-4-6"},
            headers=headers,
        )
        assert resp.status_code == 200
        # We can't directly inspect the IP used, but the request should succeed.
        # Verifying _resolve_client_ip more directly:
        from proxy.main import _resolve_client_ip

        mock_request = MagicMock()
        mock_request.headers = {"X-Forwarded-For": "203.0.113.50, 10.0.0.1"}
        assert _resolve_client_ip(mock_request) == "203.0.113.50"

    def test_forwarded_for_ignored_by_default(self, monkeypatch):
        from proxy.main import _resolve_client_ip

        mock_request = MagicMock()
        mock_request.headers = {"X-Forwarded-For": "203.0.113.50, 10.0.0.1"}
        mock_request.client.host = "127.0.0.1"

        monkeypatch.delenv("ARGUS_TRUST_PROXY_HEADERS", raising=False)
        assert _resolve_client_ip(mock_request) == "127.0.0.1"

    def test_resolve_real_ip_fallback(self, monkeypatch):
        from proxy.main import _resolve_client_ip

        mock_request = MagicMock()
        mock_request.headers = {"X-Real-IP": "198.51.100.7"}

        monkeypatch.setenv("ARGUS_TRUST_PROXY_HEADERS", "yes")
        assert _resolve_client_ip(mock_request) == "198.51.100.7"

    def test_resolve_client_host_fallback(self):
        from proxy.main import _resolve_client_ip

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "127.0.0.1"
        assert _resolve_client_ip(mock_request) == "127.0.0.1"


class TestCorrelationId:
    """P1.1 — response includes a request_id."""

    @patch("proxy.main.client")
    def test_response_has_request_id(self, mock_client, tc: TestClient):
        mock_client.messages.create.return_value = _mock_anthropic_response("world")

        resp = tc.post(
            "/generate",
            json={"prompt": "hello", "model": "claude-sonnet-4-6"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "request_id" in data
        # Must be a valid UUID
        uuid.UUID(data["request_id"])
        assert data["provider"] == "anthropic"
        assert data["model"] == "claude-sonnet-4-6"
