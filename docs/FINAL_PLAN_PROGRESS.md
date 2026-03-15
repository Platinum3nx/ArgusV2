# ArgusV2 Final Plan Progress

Last updated: 2026-03-15 (UTC)

This tracker maps implementation progress to the 5 phases defined in `FinalPlan.md`.

---

## Phase 1 — Core Reliability & Correctness
**Status:** IN PROGRESS (hardening pass active)

### Goal
Stabilize end-to-end autonomous behavior so outcomes are deterministic, fail-closed, and reproducible.

### Completed in this pass
- ✅ Removed non-production-safe CI tolerance by making MR verification non-optional in `.gitlab-ci.yml` (no `allow_failure` for `argus-verify`).
- ✅ Strengthened CI loop detection from string matching to AST parsing in `src/core/ci_integrity.py`.
- ✅ Replaced unsafe loop translation fallback behavior in `src/core/translator/dafny_translator.py` with explicit fail-closed behavior when deterministic loop lowering is unavailable.
- ✅ Updated translator regression test to enforce fail-closed loop behavior (`tests/test_dafny_translator.py`).

### Remaining for Phase 1 completion
- [ ] Implement deterministic loop lowering for Dafny path (remove current fail-closed limitation).
- [ ] Execute full local test suite in a provisioned environment (python/pytest + Lean/Dafny toolchain availability).
- [ ] Produce benchmarked reliability metrics doc (`docs/reliability-report.md`) from real repeated runs.
- [ ] Validate artifact completeness against all outcome paths (VERIFIED/FIXED/VULNERABLE/UNVERIFIED/ERROR).
- [ ] Run seeded benchmark corpus and record evidence links/output hashes.

### Evidence
- `src/core/translator/dafny_translator.py`
- `src/core/ci_integrity.py`
- `.gitlab-ci.yml`
- `tests/test_dafny_translator.py`

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
