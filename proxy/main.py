"""Argus LLM Proxy — forwards requests to Anthropic with a server-held API key."""

from __future__ import annotations

import os

import anthropic
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

PROXY_TOKEN = os.environ.get("ARGUS_PROXY_TOKEN", "")
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


class GenerateRequest(BaseModel):
    prompt: str
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096


class GenerateResponse(BaseModel):
    text: str


@app.post("/generate", response_model=GenerateResponse)
def generate(
    body: GenerateRequest,
    x_argus_token: str = Header(default=""),
) -> GenerateResponse:
    if not PROXY_TOKEN or x_argus_token != PROXY_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    response = client.messages.create(
        model=body.model,
        max_tokens=body.max_tokens,
        messages=[{"role": "user", "content": body.prompt}],
    )
    text = (response.content[0].text or "").strip()
    return GenerateResponse(text=text)
