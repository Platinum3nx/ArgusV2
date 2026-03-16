from __future__ import annotations

import os
from typing import Optional


class ConfigurationError(Exception):
    """Raised when LLM provider is misconfigured. Pipeline must not start."""


class LLMClient:
    """
    Base contract for all LLM provider clients.

    All LLM interaction in ArgusV2 goes through this interface.
    The single method `generate(contents) -> str` is intentionally minimal —
    all 4 call sites send a flat prompt string and receive a flat text response.
    """

    provider_name: str  # "anthropic" or "gemini" — recorded in provenance
    model_id: str       # e.g. "claude-sonnet-4-6" or "gemini-2.5-pro"

    def generate(self, contents: str) -> str:
        """
        Send a prompt string and return the text response.
        Raises on API failure — callers are responsible for exception handling.
        """
        raise NotImplementedError


class AnthropicClient(LLMClient):
    """Anthropic Claude backend."""

    def __init__(self, api_key: str, model: str) -> None:
        import anthropic as _anthropic  # validated present by factory

        self._client = _anthropic.Anthropic(api_key=api_key)
        self.provider_name = "anthropic"
        self.model_id = model

    def generate(self, contents: str) -> str:
        response = self._client.messages.create(
            model=self.model_id,
            max_tokens=4096,
            messages=[{"role": "user", "content": contents}],
        )
        return (response.content[0].text or "").strip()


class GeminiClient(LLMClient):
    """Google Gemini backend."""

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai as _genai  # validated present by factory

        self._client = _genai.Client(api_key=api_key)
        self.provider_name = "gemini"
        self.model_id = model

    def generate(self, contents: str) -> str:
        response = self._client.models.generate_content(model=self.model_id, contents=contents)
        return (response.text or "").strip()


def create_llm_client(provider: str, model: Optional[str] = None) -> LLMClient:
    """
    Factory for LLM provider clients.

    Configuration schema and precedence:
      LLM_PROVIDER env var  <  CLI --provider  <  PipelineConfig.provider

    Required credentials per provider:
      anthropic: ANTHROPIC_API_KEY
      gemini:    GEMINI_API_KEY

    Raises ConfigurationError if:
      - The requested provider is unknown
      - The required API key env var is not set
      - The required SDK is not installed

    Credentials are validated here at construction time so failures surface
    immediately at pipeline startup, not silently mid-run.
    """
    if provider == "anthropic":
        resolved_model = model or "claude-sonnet-4-6"
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY is not set. "
                "Set this environment variable to use the Anthropic provider, "
                "or switch to --provider gemini with GEMINI_API_KEY."
            )
        try:
            import anthropic as _  # noqa: F401
        except ImportError as exc:
            raise ConfigurationError(
                "anthropic SDK is not installed. Run: pip install anthropic"
            ) from exc
        return AnthropicClient(api_key=api_key, model=resolved_model)

    if provider == "gemini":
        resolved_model = model or "gemini-2.5-pro"
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY is not set. "
                "Set this environment variable to use the Gemini provider, "
                "or switch to --provider anthropic with ANTHROPIC_API_KEY."
            )
        try:
            from google import genai as _  # noqa: F401
        except ImportError as exc:
            raise ConfigurationError(
                "google-genai SDK is not installed. Run: pip install google-genai"
            ) from exc
        return GeminiClient(api_key=api_key, model=resolved_model)

    raise ConfigurationError(
        f"Unknown LLM provider '{provider}'. Supported values: anthropic, gemini."
    )
