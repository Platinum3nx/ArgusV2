# ArgusV2 Reliability Report

Status: Phase 5 consolidated update (2026-03-24 UTC)

## Scope
Consolidated reliability evidence across Phase 1 and Phase 3+4 outcomes, including fail-closed behavior, verdict stability, and CI integrity gates.

## Consolidated metrics
| Metric | Phase 1 | Phase 3/4 | Target | Status |
|---|---:|---:|---:|---|
| End-to-end success rate | 20/20 runs | 18/18 provider validation runs | >=95% | PASS |
| Safe-file verdict stability | 100% VERIFIED | 100% VERIFIED | 100% | PASS |
| Vulnerability-path stability | 100% detect (VULNERABLE/FIXED) | 100% detect (VULNERABLE/FIXED) | 100% | PASS |
| False VERIFIED rate | 0% | 0% | 0% | PASS |
| Test suite pass rate | 66/66 | 204/204 | 100% | PASS |
| Fail-closed scenario coverage | validated | 14/14 passing | all pass | PASS |

## Latency profile
- Phase 1 p50: 1370.54ms, p95: 2717.32ms (seeded reliability run)
- Phase 3 provider delta: Anthropic observed 1.9x-8.4x faster than Gemini on benchmark scenarios due to fewer re-verification cycles
- Practical CI goal: single-file audit under 5 minutes with configured provider and verifier runtime

## Retry / timeout behavior
- Provider/runtime errors produce fail-closed verdict outcomes (ERROR/UNVERIFIED/VULNERABLE path), never false VERIFIED.
- Pipeline retries are operationally driven at CI job level (GitLab retry), not hidden auto-retries that could mask nondeterminism.

## Evidence index
- `artifacts/phase1/reliability-summary.json`
- `artifacts/phase1/ci-gates.json`
- `artifacts/phase3/reliability-summary.json`
- `artifacts/phase3/anthropic_r1_safe.json`
- `artifacts/phase3/anthropic_r1_vuln.json`
- `artifacts/phase3/anthropic_r1_drift.json`
- `artifacts/phase5/mr-comment-stress.json`

## Current checkout snapshot
- Maintained suite: `pytest` or `pytest tests -q` runs `tests/` only and passes `204/204`.
- Live demo runs in this checkout: `safe_transfer.py` `VERIFIED`, `vulnerable_transfer.py` `FIXED`, `drift_withdrawal.py` `FIXED`.
- Latest observed runtimes in this checkout: `safe_transfer.py` `10.34s`, `vulnerable_transfer.py` `66.36s`, `drift_withdrawal.py` `57.43s`.
- Provider-backed reruns in this environment still depend on a configured `ARGUS_PROXY_TOKEN`.
