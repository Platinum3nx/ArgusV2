"""Argus LLM Proxy — forwards requests to Anthropic with a server-held API key."""

from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict
from typing import Dict, Tuple

import anthropic
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

app = FastAPI(title="argus-proxy", version="1.1.0")
log = logging.getLogger("argus.proxy")

DEFAULT_DAILY_LIMIT = int(os.environ.get("ARGUS_DAILY_LIMIT", "500"))
HOURLY_IP_LIMIT = int(os.environ.get("ARGUS_HOURLY_IP_LIMIT", "30"))


# ---------------------------------------------------------------------------
# Auth/token config
# ---------------------------------------------------------------------------

def _load_token_config() -> Dict[str, dict]:
    """
    Load valid caller tokens.

    Preferred env var:
      ARGUS_PROXY_TOKENS_JSON='{"tokenA": {"name": "team-a", "daily_limit": 300}}'

    Backward-compat fallback:
      ARGUS_PROXY_TOKEN='single-token'
    """
    raw = os.environ.get("ARGUS_PROXY_TOKENS_JSON", "").strip()
    if raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid ARGUS_PROXY_TOKENS_JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise RuntimeError("ARGUS_PROXY_TOKENS_JSON must be a JSON object")
        out: Dict[str, dict] = {}
        for token, cfg in parsed.items():
            if not isinstance(token, str) or not token.strip():
                continue
            cfg = cfg if isinstance(cfg, dict) else {}
            out[token.strip()] = {
                "name": str(cfg.get("name", "default")),
                "daily_limit": int(cfg.get("daily_limit", DEFAULT_DAILY_LIMIT)),
            }
        if out:
            return out

    single = os.environ.get("ARGUS_PROXY_TOKEN", "").strip()
    if single:
        return {
            single: {
                "name": "default",
                "daily_limit": DEFAULT_DAILY_LIMIT,
            }
        }
    return {}


TOKEN_CONFIG = _load_token_config()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


# ---------------------------------------------------------------------------
# In-memory rate limiting (resets on server restart — intentional)
# ---------------------------------------------------------------------------

_token_counts: dict[str, int] = defaultdict(int)
_token_reset_at: dict[str, float] = {}
_ip_counts: dict[str, int] = defaultdict(int)
_ip_reset_at: dict[str, float] = {}


def _check_token_limit(token: str) -> None:
    now = time.time()
    reset = _token_reset_at.get(token, 0.0)
    if now > reset:
        _token_counts[token] = 0
        _token_reset_at[token] = now + 86400
    limit = int(TOKEN_CONFIG[token].get("daily_limit", DEFAULT_DAILY_LIMIT))
    if _token_counts[token] >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Token daily limit ({limit}) reached. Resets in {int(_token_reset_at[token] - now)}s.",
        )
    _token_counts[token] += 1


def _check_ip_limit(ip: str) -> None:
    now = time.time()
    reset = _ip_reset_at.get(ip, 0.0)
    if now > reset:
        _ip_counts[ip] = 0
        _ip_reset_at[ip] = now + 3600
    if _ip_counts[ip] >= HOURLY_IP_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Per-IP hourly limit ({HOURLY_IP_LIMIT}) reached. Resets in {int(_ip_reset_at[ip] - now)}s.",
        )
    _ip_counts[ip] += 1


def _authorize(x_argus_token: str) -> Tuple[str, dict]:
    token = (x_argus_token or "").strip()
    if not token or token not in TOKEN_CONFIG:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token, TOKEN_CONFIG[token]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class GenerateRequest(BaseModel):
    prompt: str
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096


class GenerateResponse(BaseModel):
    text: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "argus-proxy"}


@app.get("/ready")
def ready() -> dict:
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
    has_tokens = bool(TOKEN_CONFIG)
    return {
        "ready": has_anthropic and has_tokens,
        "anthropic_key_configured": has_anthropic,
        "token_count": len(TOKEN_CONFIG),
    }


@app.post("/generate", response_model=GenerateResponse)
def generate(
    request: Request,
    body: GenerateRequest,
    x_argus_token: str = Header(default=""),
) -> GenerateResponse:
    token, token_cfg = _authorize(x_argus_token)

    client_ip = request.client.host if request.client else "unknown"
    _check_token_limit(token)
    _check_ip_limit(client_ip)

    try:
        response = client.messages.create(
            model=body.model,
            max_tokens=body.max_tokens,
            messages=[{"role": "user", "content": body.prompt}],
        )
        text = (response.content[0].text or "").strip()
        if not text:
            raise HTTPException(status_code=502, detail="Empty response from upstream model")
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - network/upstream failure
        log.exception("upstream_error token=%s model=%s", token_cfg.get("name", "unknown"), body.model)
        raise HTTPException(status_code=502, detail=f"Upstream provider error: {exc}") from exc

    log.info(
        "request_ok token=%s model=%s ip=%s chars=%d",
        token_cfg.get("name", "unknown"),
        body.model,
        client_ip,
        len(body.prompt),
    )
    return GenerateResponse(text=text)


@app.get("/usage")
def usage(x_argus_token: str = Header(default="")) -> dict:
    token, token_cfg = _authorize(x_argus_token)
    now = time.time()
    return {
        "token_name": token_cfg.get("name", "default"),
        "token_requests_today": _token_counts.get(token, 0),
        "token_daily_limit": int(token_cfg.get("daily_limit", DEFAULT_DAILY_LIMIT)),
        "token_resets_in_seconds": max(0, int(_token_reset_at.get(token, now) - now)),
        "ip_hourly_limit": HOURLY_IP_LIMIT,
    }
