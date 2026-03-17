# Argus Proxy Operations

This runbook covers hosted-key operation for `proxy/main.py`.

## Required environment variables
- `ANTHROPIC_API_KEY` — upstream model key (server-side only)
- `ARGUS_PROXY_TOKENS_JSON` — token map (preferred)
  - Example:
    ```json
    {
      "tok_team_a": {"name": "team-a", "daily_limit": 400},
      "tok_team_b": {"name": "team-b", "daily_limit": 150}
    }
    ```
- Legacy fallback: `ARGUS_PROXY_TOKEN` (single token)
- Optional: `ARGUS_DAILY_LIMIT`, `ARGUS_HOURLY_IP_LIMIT`

## Token lifecycle
1. Issue new token in `ARGUS_PROXY_TOKENS_JSON` with tenant `name` and `daily_limit`.
2. Roll token to client CI variable (`ARGUS_PROXY_TOKEN`) out-of-band.
3. Revoke by removing token from JSON and redeploying proxy.

## Operational endpoints
- `GET /health` → basic service liveness
- `GET /ready` → readiness (checks key + token config)
- `GET /usage` (auth required) → per-token daily usage and reset timer

## Security notes
- Never expose `ANTHROPIC_API_KEY` to clients.
- Use masked variables on Render/GitLab.
- Rotate tokens periodically and on suspected leakage.
- Start with conservative per-token limits and raise gradually.
