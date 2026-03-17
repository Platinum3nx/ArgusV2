from __future__ import annotations

import logging
import os
import time

import requests

log = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds: 2, 4, 8
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


# ---------------------------------------------------------------------------
# Proxy configuration
# ---------------------------------------------------------------------------
DEFAULT_PROXY_URL = "https://argusv2-0.onrender.com"


class ConfigurationError(Exception):
    """Raised when LLM provider is misconfigured. Pipeline must not start."""


class LLMClient:
    """
    Base contract for the LLM provider client.

    All LLM interaction in ArgusV2 goes through this interface.
    The single method `generate(contents) -> str` is intentionally minimal —
    all 4 call sites send a flat prompt string and receive a flat text response.
    """

    provider_name: str  # "anthropic" — recorded in provenance
    model_id: str       # e.g. "claude-sonnet-4-6"

    def generate(self, contents: str) -> str:
        """
        Send a prompt string and return the text response.
        Raises on API failure — callers are responsible for exception handling.
        """
        raise NotImplementedError


class ProxyClient(LLMClient):
    """Calls the hosted Argus proxy which holds the Anthropic API key."""

    def __init__(self, model: str, proxy_url: str, proxy_token: str) -> None:
        self.provider_name = "anthropic"
        self.model_id = model
        self.proxy_url = proxy_url
        self.proxy_token = proxy_token

    def generate(self, contents: str) -> str:
        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(
                    f"{self.proxy_url}/generate",
                    json={
                        "prompt": contents,
                        "model": self.model_id,
                        "max_tokens": 4096,
                    },
                    headers={"X-Argus-Token": self.proxy_token},
                    timeout=120,
                )
                if response.status_code not in RETRYABLE_STATUS:
                    response.raise_for_status()
                    return response.json()["text"]
                last_exc = requests.HTTPError(response=response)
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_exc = exc

            wait = BACKOFF_BASE ** attempt
            log.warning("Proxy request failed (attempt %d/%d), retrying in %ds…", attempt, MAX_RETRIES, wait)
            time.sleep(wait)

        raise last_exc  # type: ignore[misc]


def create_llm_client(provider: str | None = None, model: str | None = None) -> LLMClient:
    """
    Create the proxy-backed LLM client.

    Hosted mode is Anthropic-only. `provider` is accepted for backward compatibility
    with older call sites and CLI arguments.
    """
    resolved_provider = (provider or "anthropic").strip().lower()
    if resolved_provider not in {"anthropic", ""}:
        raise ConfigurationError(
            f"Provider '{resolved_provider}' is not supported in hosted mode. "
            "Use --provider anthropic."
        )

    proxy_token = os.getenv("ARGUS_PROXY_TOKEN", "").strip()
    proxy_url = os.getenv("ARGUS_PROXY_URL", DEFAULT_PROXY_URL).rstrip("/")

    if not proxy_token:
        raise ConfigurationError(
            "ARGUS_PROXY_TOKEN is not set. Configure this environment variable to use hosted Argus."
        )

    resolved_model = model or "claude-sonnet-4-6"
    return ProxyClient(model=resolved_model, proxy_url=proxy_url, proxy_token=proxy_token)
