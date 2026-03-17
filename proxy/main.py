"""Argus LLM Proxy — forwards requests to Anthropic with a server-held API key."""

from __future__ import annotations

import os
import time
from collections import defaultdict

import anthropic
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()

PROXY_TOKEN = os.environ.get("ARGUS_PROXY_TOKEN", "")
DAILY_GLOBAL_LIMIT = int(os.environ.get("ARGUS_DAILY_LIMIT", "500"))
HOURLY_IP_LIMIT = int(os.environ.get("ARGUS_HOURLY_IP_LIMIT", "30"))

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


# ---------------------------------------------------------------------------
# In-memory rate limiting (resets on server restart — intentional)
# ---------------------------------------------------------------------------

_global_count = 0
_global_reset_at = 0.0
_ip_counts: dict[str, int] = defaultdict(int)
_ip_reset_at: dict[str, float] = {}


def _check_global_limit() -> None:
    global _global_count, _global_reset_at
    now = time.time()
    if now > _global_reset_at:
        _global_count = 0
        _global_reset_at = now + 86400  # 24 hours
    if _global_count >= DAILY_GLOBAL_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Global daily limit ({DAILY_GLOBAL_LIMIT} requests) reached. Resets in {int(_global_reset_at - now)}s.",
        )
    _global_count += 1


def _check_ip_limit(ip: str) -> None:
    now = time.time()
    reset = _ip_reset_at.get(ip, 0.0)
    if now > reset:
        _ip_counts[ip] = 0
        _ip_reset_at[ip] = now + 3600  # 1 hour
    if _ip_counts[ip] >= HOURLY_IP_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Per-IP hourly limit ({HOURLY_IP_LIMIT} requests) reached. Resets in {int(_ip_reset_at[ip] - now)}s.",
        )
    _ip_counts[ip] += 1


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


@app.post("/generate", response_model=GenerateResponse)
def generate(
    request: Request,
    body: GenerateRequest,
    x_argus_token: str = Header(default=""),
) -> GenerateResponse:
    if not PROXY_TOKEN or x_argus_token != PROXY_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    client_ip = request.client.host if request.client else "unknown"
    _check_global_limit()
    _check_ip_limit(client_ip)

    response = client.messages.create(
        model=body.model,
        max_tokens=body.max_tokens,
        messages=[{"role": "user", "content": body.prompt}],
    )
    text = (response.content[0].text or "").strip()
    return GenerateResponse(text=text)


@app.get("/usage")
def usage(x_argus_token: str = Header(default="")) -> dict:
    if not PROXY_TOKEN or x_argus_token != PROXY_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    now = time.time()
    return {
        "global_requests_today": _global_count,
        "global_limit": DAILY_GLOBAL_LIMIT,
        "global_resets_in_seconds": max(0, int(_global_reset_at - now)),
    }
