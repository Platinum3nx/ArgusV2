from __future__ import annotations

import logging
import os
import random
import time

import requests

log = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds: 2, 4, 8
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
DEFAULT_CONNECT_TIMEOUT_SECONDS = 5.0
DEFAULT_READ_TIMEOUT_SECONDS = 45.0


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

    def __init__(
        self,
        model: str,
        proxy_url: str,
        proxy_token: str,
        connect_timeout_seconds: float = DEFAULT_CONNECT_TIMEOUT_SECONDS,
        read_timeout_seconds: float = DEFAULT_READ_TIMEOUT_SECONDS,
    ) -> None:
        self.provider_name = "anthropic"
        self.model_id = model
        self.proxy_url = proxy_url
        self.proxy_token = proxy_token
        self.connect_timeout_seconds = max(1.0, float(connect_timeout_seconds))
        self.read_timeout_seconds = max(1.0, float(read_timeout_seconds))

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
                    timeout=(self.connect_timeout_seconds, self.read_timeout_seconds),
                )
                if response.status_code not in RETRYABLE_STATUS:
                    response.raise_for_status()
                    payload = response.json()
                    if not isinstance(payload, dict) or "text" not in payload:
                        raise ValueError(f"Proxy response missing 'text' field: {list(payload.keys()) if isinstance(payload, dict) else type(payload)}")
                    text = payload["text"]
                    if not isinstance(text, str) or not text.strip():
                        raise ValueError("Proxy returned empty or non-string 'text'.")
                    request_id = payload.get("request_id", "")
                    if request_id:
                        log.info("proxy_request_id=%s", request_id)
                    return text
                last_exc = requests.HTTPError(response=response)
            except (requests.ConnectionError, requests.Timeout, ValueError) as exc:
                last_exc = exc

            if attempt == MAX_RETRIES:
                break

            # Honor Retry-After header if present on 429 responses
            retry_after = None
            if isinstance(last_exc, requests.HTTPError) and hasattr(last_exc, 'response') and last_exc.response is not None:
                retry_after = last_exc.response.headers.get("Retry-After")

            if retry_after is not None:
                try:
                    wait = min(float(retry_after), 60)
                except (ValueError, TypeError):
                    wait = BACKOFF_BASE ** attempt
            else:
                wait = BACKOFF_BASE ** attempt

            # Add bounded jitter: +/- 25% of base wait
            jitter = wait * 0.25 * (2 * random.random() - 1)
            wait = max(1, wait + jitter)

            log.warning("Proxy request failed (attempt %d/%d), retrying in %.1fs…", attempt, MAX_RETRIES, wait)
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
    connect_timeout_seconds = _read_timeout_env(
        "ARGUS_PROXY_CONNECT_TIMEOUT_SECONDS",
        DEFAULT_CONNECT_TIMEOUT_SECONDS,
    )
    read_timeout_seconds = _read_timeout_env(
        "ARGUS_PROXY_READ_TIMEOUT_SECONDS",
        DEFAULT_READ_TIMEOUT_SECONDS,
    )

    if not proxy_token:
        raise ConfigurationError(
            "ARGUS_PROXY_TOKEN is not set. Configure this environment variable to use hosted Argus."
        )

    resolved_model = model or "claude-sonnet-4-6"
    return ProxyClient(
        model=resolved_model,
        proxy_url=proxy_url,
        proxy_token=proxy_token,
        connect_timeout_seconds=connect_timeout_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )


def _read_timeout_env(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default

    try:
        value = float(raw)
    except ValueError:
        log.warning("Invalid %s=%r; using default %.1fs", name, raw, default)
        return default

    if value <= 0:
        log.warning("Non-positive %s=%r; using default %.1fs", name, raw, default)
        return default
    return value
