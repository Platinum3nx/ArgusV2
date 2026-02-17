# ArgusV2 Execution Board

## Sprint Scope
- Scope: Phase 1 + Phase 2 + Phase 3 from `/Users/arjunmalghan/ArgusV2/README2.md`
- Verification runtime: Docker-first (toolchains pinned in container)
- LLM mode: Real Gemini calls enabled for discovery/repair modules
- Gate model: Staged gates (core blocking now, mutation/reproducibility before sprint close)

## Agent Team
- Agent A (`GitLab Integration`): `src/adapters/gitlab_adapter.py`, MR comment/label publishing behavior, adapter tests
- Agent B (`CI/Gates`): `src/core/ci_integrity.py`, CLI CI-mode enforcement, mutation + seeded corpus gate checks
- Agent C (`Delivery/Packaging`): `.gitlab-ci.yml`, `.gitlab/duo/agent-config.yml`, `config.yml`, artifact contract wiring
- Agent D (`QA/Regression`): tests for adapter/reporter/CI integrity + full suite pass before milestone close

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
- Status: `COMPLETED`
- Objective: Enforce CI-style integrity checks for Phase 1+2 deliverable.
- Tasks:
  - [x] Determinism checks for canonical obligation hashing
  - [x] Assumption evidence coverage gate
  - [x] Unsupported construct fail-closed behavior tests
  - [x] Reproducibility test harness
  - [x] Mutation gate baseline
  - [x] Commit + push milestone

### Milestone 4: Phase 3 GitLab Integration
- Status: `IN PROGRESS`
- Objective: Add GitLab platform integration, CI gates runner, and deployable Duo flow configuration.
- Tasks:
  - [x] Build GitLab adapter (`src/adapters/gitlab_adapter.py`)
  - [x] Create Duo Custom Flow configuration (`config.yml`, `.gitlab/duo/agent-config.yml`)
  - [x] Create `.gitlab-ci.yml` for CI-based triggering + artifacts
  - [x] Implement CI integrity gates runner (unsupported, determinism, evidence, semantic, proof, verdict, traceability, reproducibility)
  - [x] Add seeded benchmark corpus + mutation gate integration
  - [x] Add tests for Phase 3 modules
  - [ ] Test end-to-end on a real GitLab MR (requires external GitLab project/token context)
  - [ ] Deploy to GitLab AI Catalog (requires external publish credentials/process)
  - [x] Commit + push milestone (local implementation checkpoint)

## Risks / Blockers
- Lean/Dafny binaries may be unavailable locally; verifier tests will mock subprocess.
- Real Gemini calls require valid runtime key and network during integration smoke tests.
- Real GitLab MR E2E validation needs a live GitLab project + CI run context not available in local unit test environment.
- GitLab AI Catalog deployment is an external release operation and cannot be completed from local repo-only workflow.

## Progress Log
- 2026-02-17: Sprint started. Board created and milestone plan established.
- 2026-02-17: Milestone 1 completed. Added trusted core modules and tests (`16 passed`).
- 2026-02-17: Milestone 2 completed. Added pipeline, translators/verifiers, repair, reporter, CLI, and expanded tests (`31 passed`).
- 2026-02-17: Milestone 3 completed. Added staged quality gates and gate tests (`37 passed`).
- 2026-02-17: Phase 3 implementation started with agent team split (GitLab adapter, CI gate runner, Duo/CI configs, QA).
- 2026-02-17: Added GitLab adapter, SARIF + GitLab SAST outputs, CI integrity suite, seeded benchmark corpus, and new tests (`43 passed`).
