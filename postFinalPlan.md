# postFinalPlan.md — ArgusV2 Technical Hardening Plan (Post FinalPlan)

Date: 2026-03-19
Purpose: Close remaining technical risk before submission and improve real-world product reliability for engineering teams.

---

## Goals

1. Eliminate correctness ambiguity in UI and CI integrity checks.
2. Harden hosted proxy behavior for abuse resistance and operational reliability.
3. Increase confidence via targeted failure-mode testing.
4. Improve production readiness (token lifecycle, observability, quotas).

---

## Priority P0 (Must-Do ASAP)

### P0.1 — Fix Dashboard obligation default status (PASS -> UNKNOWN)

**Problem**
`src/core/dashboard.py` currently defaults missing obligation results to `PASS`:
- `verified = result_map.get(obl_id, True)`

If result data is absent, UI can mislead users into thinking an obligation passed.

**Fix**
- Change default from `True` to `None`/unknown sentinel.
- Render statuses as:
  - `PASS` (green)
  - `FAIL` (red)
  - `N/A` or `UNKNOWN` (neutral warning style)
- Add a short legend/explanatory tooltip: “UNKNOWN = no verifier result found for this obligation.”

**Acceptance Criteria**
- No obligation row is marked PASS when no matching verifier result exists.
- Dashboard tests include a missing-result case and assert `UNKNOWN` rendering.

---

### P0.2 — Fix mutation gate verifier-routing mismatch

**Problem**
In `src/core/ci_integrity.py::_evaluate_mutation_with_lean`, loop cases may be translated through Dafny but still verified with Lean.

**Fix**
- Route verifier based on translation language:
  - Lean translation -> `LeanVerifier`
  - Dafny translation -> `DafnyVerifier`
- Or enforce lean-only mutation policy and explicitly skip/flag non-lean path.

**Acceptance Criteria**
- Mutation evaluation never uses a verifier that does not match translation output language.
- New tests cover loop mutation path and assert correct verifier routing.

---

### P0.3 — Proxy request size guardrails

**Problem**
Proxy currently has no strict prompt-size gate.

**Fix**
- Add env-configurable limits:
  - `ARGUS_MAX_PROMPT_CHARS` (e.g., default 80k)
  - optional `ARGUS_MAX_TOKENS_REQUESTED` upper bound clamp
- Reject oversized requests with 413 or 422 and clear error message.

**Acceptance Criteria**
- Oversized prompt requests are rejected deterministically.
- Limits are documented in proxy ops runbook.

---

### P0.4 — Retry behavior hardening (Retry-After + jitter)

**Problem**
Client backoff is deterministic and ignores `Retry-After`.

**Fix**
- In `src/core/llm_provider.py`:
  - If response is 429 and has `Retry-After`, honor it.
  - Add bounded jitter to backoff to avoid synchronized retries.

**Acceptance Criteria**
- Unit tests verify:
  - `Retry-After` is respected
  - jittered backoff remains within bounded range

---

## Priority P1 (Strongly Recommended)

### P1.1 — Add end-to-end correlation IDs

**Fix**
- Proxy generates `request_id` per request.
- Return `request_id` in proxy response payload.
- Include `request_id` in client logs and trace artifacts (`result.json`/summary metadata where relevant).

**Acceptance Criteria**
- Any failed request can be traced from CI logs to proxy logs via request_id.

---

### P1.2 — Expand hosted-mode integration tests (failure-path focused)

**Add tests for**
- Unauthorized token (401)
- Quota exceeded/rate limit (429)
- Upstream provider failure (502 path)
- Malformed payload from proxy
- Timeout -> retry -> success

**Acceptance Criteria**
- Tests assert fail-closed outcomes and expected error surfaces in CLI/pipeline.

---

### P1.3 — Proxy response schema tightening

**Fix**
- Standardize proxy `/generate` response shape:
  - `text`
  - `request_id`
  - `provider`
  - `model`
  - optional `token_name`
- Validate via Pydantic model.

**Acceptance Criteria**
- Client/parser rejects schema drift cleanly.
- Tests assert schema contract stability.

---

## Priority P2 (Product/Scale Readiness)

### P2.1 — Persistent quotas and usage accounting

**Problem**
Current usage/limits are in-memory and reset on restart.

**Fix**
- Move counters to Redis/Postgres.
- Preserve per-token daily/hourly accounting across restarts.

**Acceptance Criteria**
- Restart does not reset token usage counters.

---

### P2.2 — Token lifecycle tooling

**Fix**
- Add admin tooling/API for:
  - issue token
  - revoke token
  - rotate token
  - set per-token limits

**Acceptance Criteria**
- Token rotation/revocation can happen without risky manual JSON edits.

---

### P2.3 — Supported-pattern detector + user guidance

**Fix**
- Early classification of unsupported constructs.
- Return explicit actionable guidance instead of opaque UNVERIFIED paths.

**Acceptance Criteria**
- Engineers get deterministic “why + what next” messaging for unsupported code.

---

## Execution Plan (6-Day Focus)

### Day 1
- P0.1 Dashboard UNKNOWN status
- P0.2 Mutation verifier routing fix
- Add/update tests for both

### Day 2
- P0.3 Proxy request size guardrails
- P0.4 Retry-After + jitter in client
- Add tests

### Day 3
- P1.2 Hosted failure-mode integration tests
- P1.3 Proxy response schema contract hardening

### Day 4
- P1.1 Correlation IDs end-to-end
- Update trace/report documentation

### Day 5-6 (if time)
- P2.1 persistent usage backend (minimum viable)
- P2.2 token lifecycle admin script/API

---

## Definition of Done (Technical)

- No misleading PASS statuses in dashboard.
- Mutation gate language/verifier alignment guaranteed.
- Proxy rejects oversized requests and handles 429 retries robustly.
- Hosted-mode failure-path tests pass and verify fail-closed behavior.
- Correlation IDs available across proxy + client + trace.
- Documentation updated to reflect final runtime behavior and limits.

---

## Notes

- This plan focuses on **technical trust and reliability**, not only demo polish.
- Product remains fail-closed by design; improvements target correctness, operability, and scale robustness.
