# ArgusV2 Execution Board

## Sprint Scope
- Scope: Phase 1 + Phase 2 from `/Users/arjunmalghan/ArgusV2/README2.md`
- Verification runtime: Docker-first (toolchains pinned in container)
- LLM mode: Real Gemini calls enabled for discovery/repair modules
- Gate model: Staged gates (core blocking now, mutation/reproducibility before sprint close)

## Milestones

### Milestone 1: Trusted Core Contracts
- Status: `COMPLETED`
- Objective: Build fail-closed verdicting and trusted policy/evidence/guard layers.
- Tasks:
  - [x] Create execution board
  - [x] Scaffold `src/core/` + test layout
  - [x] Implement `verdict.py` fail-closed contract
  - [x] Implement deterministic `obligation_policy.py`
  - [x] Implement `assumption_evidence.py`
  - [x] Implement `semantic_guard.py`
  - [x] Add unit tests for trusted core modules
  - [x] Commit + push milestone

### Milestone 2: Pipeline + Translation/Verification + Reporting
- Status: `COMPLETED`
- Objective: End-to-end core pipeline with trace artifacts and report generation.
- Tasks:
  - [x] Implement translator interfaces + AST/LLM/Dafny translators
  - [x] Implement verifier interfaces + Lean/Dafny verifiers + router
  - [x] Implement invariant discovery + repair modules
  - [x] Implement pipeline orchestration
  - [x] Implement reporter (JSON/Markdown)
  - [x] Implement CLI adapter
  - [x] Add end-to-end and module tests
  - [x] Commit + push milestone

### Milestone 3: Staged Quality Gates
- Status: `IN_PROGRESS`
- Objective: Enforce CI-style integrity checks for Phase 1+2 deliverable.
- Tasks:
  - [ ] Determinism checks for canonical obligation hashing
  - [ ] Assumption evidence coverage gate
  - [ ] Unsupported construct fail-closed behavior tests
  - [ ] Reproducibility test harness
  - [ ] Mutation gate baseline
  - [ ] Commit + push milestone

## Risks / Blockers
- Lean/Dafny binaries may be unavailable locally; verifier tests will mock subprocess.
- Real Gemini calls require valid runtime key and network during integration smoke tests.

## Progress Log
- 2026-02-17: Sprint started. Board created and milestone plan established.
- 2026-02-17: Milestone 1 completed. Added trusted core modules and tests (`16 passed`).
- 2026-02-17: Milestone 2 completed. Added pipeline, translators/verifiers, repair, reporter, CLI, and expanded tests (`31 passed`).
