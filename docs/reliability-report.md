# ArgusV2 Reliability Report (Phase 1)

Status: Completed
Date: 2026-03-15 UTC

## Scope
Phase 1 reliability validation for:
- deterministic obligation derivation
- semantic guard integrity
- verifier routing correctness
- trace artifact completeness
- fail-closed behavior on unsupported/translation/runtime failures

## Environment
- Repo: ArgusV2
- Python dependencies installed from `requirements.txt`
- Lean installed via `elan` (`leanprover/lean4:v4.16.0`)
- Dafny installed (`4.9.1`)

## Hardening changes delivered
1. CI merge-request verification is blocking in `.gitlab-ci.yml` (removed `allow_failure`).
2. Loop detection in CI integrity gates is AST-based (`src/core/ci_integrity.py`).
3. Deterministic Dafny loop fallback implemented for supported loop subset with explicit fail-closed behavior for unsupported patterns (`src/core/translator/dafny_translator.py`).
4. Mutation gate behavior improved for files with no generated mutations (`src/core/quality_gates.py`).
5. CI target filtering hardened to exclude non-product paths (`src/adapters/cli.py`).

## Validation results
### 1) Test suite
- Command: `PYTHONPATH=. python3 -m pytest tests -q`
- Result: `60 passed`

### 2) Repeated reliability benchmark
- Command: `PYTHONPATH=. python3 scripts/phase1_reliability_run.py`
- Result summary (`artifacts/phase1/reliability-summary.json`):
  - Runs: `20`
  - Files per run: `3`
  - Total file executions: `60`
  - p50 latency: `929.33 ms`
  - p95 latency: `1059.43 ms`
  - Max latency: `1078.07 ms`
  - Verdict stability: `true` for all seeded benchmark files
  - ERROR/UNVERIFIED outcomes: `0`

### 3) Trace artifact completeness audit
- Command: `python3 scripts/phase1_artifact_audit.py`
- Result (`artifacts/phase1/artifact-audit.json`):
  - Runs audited: `60`
  - File traces audited: `60`
  - Missing required artifacts: `0`
  - Overall: `ok=true`

### 4) CI integrity gate execution
- Command: `PYTHONPATH=. python3 scripts/phase1_ci_gate_check.py`
- Result (`artifacts/phase1/ci-gates.json`):
  - Overall gates: `passed=true`
  - Gate set: unsupported construct, obligation policy, assumption evidence, semantic guard, equivalence, proof, verdict contract, traceability, reproducibility, mutation, seeded benchmark

## Phase 1 sign-off
Phase 1 is complete against the FinalPlan acceptance intent: deterministic behavior, fail-closed contracts, reproducibility evidence, and artifact/CI integrity validation are in place and evidenced.

## Evidence index
- `docs/FINAL_PLAN_PROGRESS.md`
- `artifacts/phase1/reliability-summary.json`
- `artifacts/phase1/reliability-failures.log`
- `artifacts/phase1/artifact-audit.json`
- `artifacts/phase1/ci-gates.json`
