# ArgusV2 Final Plan Progress

Last updated: 2026-03-15 (UTC)

This tracker maps implementation progress to the 5 phases defined in `FinalPlan.md`.

---

## Phase 1 — Core Reliability & Correctness
**Status:** COMPLETED (with remediation pass 2026-03-15)

### Goal
Stabilize end-to-end autonomous behavior so outcomes are deterministic, fail-closed, and reproducible.

### Completed in initial pass
- ✅ Removed non-production-safe CI tolerance by making MR verification non-optional in `.gitlab-ci.yml` (no `allow_failure` for `argus-verify`).
- ✅ Strengthened CI loop detection from string matching to AST parsing in `src/core/ci_integrity.py`.
- ✅ Implemented deterministic Dafny loop fallback translator for supported loop forms (`for ... in range(...)` and `while` loops), replacing synthetic placeholder behavior.
- ✅ Added stricter deterministic translation rules for loop code paths: unsupported loop constructs now fail closed with explicit errors.
- ✅ Updated translator tests to validate deterministic loop fallback behavior and while-loop decreases/invariant emission (`tests/test_dafny_translator.py`).

### Completed in remediation pass (2026-03-15)
- ✅ Deterministic precondition derivation: `ObligationPolicy.derive_preconditions()` now injects `param >= 0` hypotheses for `non_negativity` obligations based on function signatures, ensuring safe code verifies without requiring LLM assumptions. `saturating_withdrawal.py` now reliably returns `VERIFIED`.
- ✅ Lean proof tactics strengthened: added `omega` tactic after `linarith` in non_negativity and bounds proof strategies for stronger integer arithmetic reasoning.
- ✅ Seeded benchmark gate extended: `expected_verdict` field added to `benchmarks/seeded/manifest.json`; gate now fails on verdict mismatches, closing the loophole where a verifier returning VULNERABLE for everything would pass all gates.
- ✅ Mutation gate redesigned: VULNERABLE files are skipped (no meaningful signal); VERIFIED files are mutation-tested with the actual Lean verifier, confirming proof sensitivity to semantic changes.
- ✅ `VerificationSummary.repaired` immutability fixed: removed direct mutation of a frozen dataclass field.
- ✅ Docker verification gap documented in `docs/reliability-report.md` (Limitations section).

### Phase 1 acceptance checklist (closed)
- [x] Deterministic/fail-closed loop translation for supported loop subset, with explicit errors for unsupported patterns.
- [x] Deterministic precondition injection for non_negativity proofs (no LLM dependency).
- [x] Safe benchmark file (`saturating_withdrawal.py`) correctly returns `VERIFIED`.
- [x] Full active test suite run in provisioned environment (`66 passed`).
- [x] Reliability benchmark run completed (`20` repeated runs over seeded corpus, stable verdicts, no ERROR/UNVERIFIED outcomes).
- [x] Artifact completeness audit completed (all required trace artifacts present).
- [x] CI integrity gate run completed with all 11 gates passing (including verdict-matching seeded benchmark gate and mutation gate).

### Evidence
- Code hardening
  - `src/core/obligation_policy.py` — `derive_preconditions()`
  - `src/core/pipeline.py` — deterministic precondition merge
  - `src/core/translator/lean_ir_emitter.py` — omega tactic
  - `src/core/ci_integrity.py` — verdict-checking benchmark gate, Lean-backed mutation gate
  - `src/core/translator/dafny_translator.py`
  - `src/core/quality_gates.py`
  - `src/adapters/cli.py`
  - `.gitlab-ci.yml`
  - `benchmarks/seeded/manifest.json` — `expected_verdict` fields
- Tests
  - `tests/test_obligation_policy.py` — `derive_preconditions` tests
  - `tests/test_ci_integrity.py` — verdict mismatch gate tests
  - `tests/test_dafny_translator.py`
  - `tests/test_cli_adapter.py`
  - `tests/` full suite (`66 passed`)
- Phase 1 execution artifacts
  - `artifacts/phase1/reliability-summary.json`
  - `artifacts/phase1/reliability-failures.log`
  - `artifacts/phase1/artifact-audit.json`
  - `artifacts/phase1/ci-gates.json`
- Phase 1 docs
  - `docs/reliability-report.md`
  - `docs/phase1-remediation-plan.md`

---

## Phase 2 — Custom Public Agent/Flow Closure
**Status:** NOT STARTED (in this pass)

### Planned work
- [ ] Add explicit README proof section for custom public agent/flow.
- [ ] Add reproducible run steps and submission wording.
- [ ] Capture demo evidence references.

---

## Phase 3 — Anthropic Impact Track
**Status:** NOT STARTED (in this pass)

### Planned work
- [ ] Provider abstraction (`anthropic|gemini|hybrid`).
- [ ] Provenance in trace/report artifacts.
- [ ] Anthropic-mode benchmark and fail-closed fallback checks.

---

## Phase 4 — UX, Frontend, and Demo Polish
**Status:** NOT STARTED (in this pass)

### Planned work
- [ ] Mission Control UI polish.
- [ ] Final MR summary/report templates.
- [ ] 3-minute deterministic demo script + fallback assets.

---

## Phase 5 — Submission Packaging & Launch Readiness
**Status:** NOT STARTED (in this pass)

### Planned work
- [ ] Complete launch-readiness gates A–G with linked evidence docs.
- [ ] Final clean-environment install + dry-run validation.
- [ ] Final submission packaging and checklist closure.
