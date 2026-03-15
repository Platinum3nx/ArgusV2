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

### Phase 1 remediation pass (2026-03-15)
6. Deterministic precondition derivation added to `ObligationPolicy.derive_preconditions()` — injects `param >= 0` hypotheses for `non_negativity` obligations without requiring LLM availability. Safe code (e.g. `saturating_withdrawal.py`) now reliably returns `VERIFIED`.
7. `omega` tactic added to non_negativity and bounds proof strategies in `LeanIREmitter` for stronger integer arithmetic reasoning.
8. Seeded benchmark gate extended with `expected_verdict` validation — the gate now fails when a pipeline report's verdict mismatches the declared expected outcome in `benchmarks/seeded/manifest.json`.
9. Mutation gate redesigned: VULNERABLE files are skipped (no meaningful signal); VERIFIED files are mutation-tested using the actual Lean verifier to confirm proof sensitivity.
10. `VerificationSummary.repaired` direct mutation fixed — replaced with dataclass construction to preserve immutability.

## Limitations
- **All benchmarks run with `require_docker_verify=False`** (local Lean invocation). Production deployments that enforce `require_docker_verify=True` will have higher latency and require a Docker image with Lean/Mathlib pre-installed. Latency numbers in this report (~1–10s) reflect local Lean execution, not containerized verification.
- Mutation testing uses simple lexical mutations (operator/keyword substitutions). More complex semantic mutations (e.g. loop body changes, arithmetic rewrites) are not covered.
- Equivalence checking uses random input sampling over `[-6, 6]`; extreme values and boundary cases are not fully covered.

## Validation results
### 1) Test suite
- Command: `PYTHONPATH=. pytest tests -q`
- Result: `66 passed`

### 2) Repeated reliability benchmark
- Command: `PYTHONPATH=. python3 scripts/phase1_reliability_run.py`
- Result summary (`artifacts/phase1/reliability-summary.json`):
  - Runs: `20`
  - Files per run: `3`
  - Total file executions: `60`
  - p50 latency: `1370.54 ms`
  - p95 latency: `2717.32 ms`
  - Max latency: `9532.97 ms`
  - Verdict stability: `true` for all seeded benchmark files
  - ERROR/UNVERIFIED outcomes: `0`
  - **Safe file verdict**: `VERIFIED` (confirmed — `saturating_withdrawal.py` proof succeeds)

### 3) Trace artifact completeness audit
- Command: `python3 scripts/phase1_artifact_audit.py`
- Result (`artifacts/phase1/artifact-audit.json`):
  - Runs audited: `192`
  - File traces audited: `198`
  - Missing required artifacts: `0`
  - Overall: `ok=true`

### 4) CI integrity gate execution
- Command: `PYTHONPATH=. python3 scripts/phase1_ci_gate_check.py`
- Result (`artifacts/phase1/ci-gates.json`):
  - Overall gates: `passed=true`
  - Gate set: unsupported construct, obligation policy, assumption evidence, semantic guard, equivalence, proof, verdict contract, traceability, reproducibility, mutation, seeded benchmark
  - Seeded benchmark verdict check: `safe/saturating_withdrawal.py → VERIFIED`, `vulnerable/negative_withdrawal.py → VULNERABLE`

## Phase 1 sign-off
Phase 1 is complete against the FinalPlan acceptance intent: deterministic behavior, fail-closed contracts, reproducibility evidence, and artifact/CI integrity validation are in place and evidenced. The remediation pass additionally confirms that safe code correctly returns VERIFIED and that CI gates enforce verdict correctness end-to-end.

## Evidence index
- `docs/FINAL_PLAN_PROGRESS.md`
- `artifacts/phase1/reliability-summary.json`
- `artifacts/phase1/reliability-failures.log`
- `artifacts/phase1/artifact-audit.json`
- `artifacts/phase1/ci-gates.json`
