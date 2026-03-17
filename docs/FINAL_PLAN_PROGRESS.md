# ArgusV2 Final Plan Progress

Last updated: 2026-03-17 (UTC)

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
**Status:** IN PROGRESS (implementation complete; visibility validation pending)

### Execution status
- [x] **Step 2.1**: Enriched `config.yml` with tools/triggers/actions declarations; enriched `.gitlab/duo/agent-config.yml` with env contract and runtime/resource notes.
- [x] **Step 2.2**: Created `.gitlab/duo/flows/argus_verify.yml` — formal flow definition mapped to `ArgusPipeline` + CI execution.
- [x] **Step 2.3**: Added README "Custom Public Agent & Flow" proof section with 60-second checklist, file-path map, trigger proof.
- [x] **Step 2.4**: Added `docs/quickstart.md` — reproducible fork-to-observed-action instructions.
- [x] **Step 2.5**: Added `docs/submission-text.md` — Devpost-ready requirement statement and judge FAQ.
- [ ] **Step 2.6**: Validate public visibility manually (repo in hackathon group, public visibility, default branch contains flow files, no exposed secrets).

### Phase 2 evidence
- `config.yml`
- `.gitlab/duo/agent-config.yml`
- `.gitlab/duo/flows/argus_verify.yml`
- `README.md` (top-level Custom Public Agent & Flow section)
- `docs/quickstart.md`
- `docs/submission-text.md`

---

## Phase 3 — Anthropic Impact Track
**Status:** COMPLETED (2026-03-16)

### Execution status

- [x] **Step 3.1**: Created `src/core/llm_provider.py` — `LLMClient` contract, `AnthropicClient`, `GeminiClient`, `create_llm_client()` factory with fail-closed `ConfigurationError` on missing keys/SDK. Fixed `GeminiClient` to store client at `__init__` (was re-instantiating per call).
- [x] **Step 3.2**: Extended `PipelineConfig` (`provider: str = "anthropic"`, model default changed to `"claude-sonnet-4-6"`) and CLI (`--provider`, `--model` arguments with env-var fallback).
- [x] **Step 3.3**: Refactored 4 call sites (`invariant_discovery.py`, `repair.py`, `proof_search.py`, `llm_translator.py`) — zero direct `genai` imports, all LLM calls via `self.llm_client.generate()`.
- [x] **Step 3.4**: Structured provenance (`provider`, `model`) in trace manifests, per-file `result.json`, `summary.json`, `argus_report.json`, SARIF `tool.driver.properties`, and MR comment footer.
- [x] **Step 3.5**: Added `anthropic>=0.40.0` to `requirements.txt`.
- [x] **Step 3.6**: Tests + fail-closed scenarios — 83 tests passing. New tests cover:
  - `tests/test_llm_provider.py`: factory (Anthropic + Gemini success paths), missing key ×2, empty key ×2, unknown provider, missing SDK (8 tests)
  - `tests/test_repair.py`: empty response, exception propagation (2 new)
  - `tests/test_llm_translator.py`: empty response, exception propagation (2 new)
  - `tests/test_invariant_discovery.py`: malformed LLM output, exception propagation (2 new)
  - `tests/test_proof_search.py`: empty response, exception propagation (2 new)
- [x] **Step 3.7**: Updated `config.yml` (Anthropic primary), `agent-config.yml` (`ANTHROPIC_API_KEY` required, `GEMINI_API_KEY` optional), `docs/submission-text.md` (Anthropic Impact Track section), `src/prompts/discover_invariants.md` (explicit schema rules).
- [x] **Step 3.8**: End-to-end validation COMPLETE. Anthropic: 3 runs × 3 files, all correct verdicts (VERIFIED/FIXED/VULNERABLE), 0 false positives, provenance in all artifacts. Gemini backward-compat: 3 runs × 3 files, same verdicts. Latency delta documented: Anthropic 1.9–8.4× faster than Gemini (fewer Lean re-verification cycles due to higher-quality first-attempt suggestions).

### Additional fixes applied during Phase 3 execution

- **Soundness fix**: `InvariantDiscovery._parse_assumptions()` now filters LLM assumptions with: (a) empty `property`, (b) invalid `source_type`, or (c) inter-parameter relationship constraints (e.g., `balance >= amount`). Such constraints represent business logic guards that must exist in code — accepting them as LLM assumptions caused false VERIFIED verdicts.
- **Prompt hardening**: `src/prompts/discover_invariants.md` updated with explicit schema rules, valid `source_type` values, and explicit prohibition against inter-parameter constraint invention.
- **CI gate fix**: `_seeded_benchmark_gate` now accepts FIXED when VULNERABLE is expected — FIXED means vulnerability was found AND repair succeeded, which satisfies a blocking verdict expectation.

### Phase 3 evidence

- `src/core/llm_provider.py` — provider contract + factory
- Diff of 4 refactored call-site files (zero `genai` references)
- `tests/test_llm_provider.py` — 8 factory tests (Anthropic + Gemini success paths + all fail-closed scenarios)
- Full test suite: `83 passed` (`pytest tests/`)
- `artifacts/phase3/reliability-summary.json` — Anthropic (3 runs) + Gemini (3 runs) evidence, latency delta
- Anthropic run artifacts: `artifacts/phase3/anthropic_r{1,2,3}_{safe,vuln,drift}.json`
- Gemini run artifacts: `artifacts/phase3/gemini_r{1,2,3}_{safe,vuln,drift}.json`
- Provenance verified: `provider` + `model` in manifests, per-file results, JSON report, SARIF

### Phase 3 acceptance criteria status

- [x] `--provider anthropic` with `ANTHROPIC_API_KEY` drives full pipeline
- [x] Default provider is `"anthropic"` everywhere (config, CLI, docs, env var default)
- [x] `--provider gemini` with `GEMINI_API_KEY` still works (2 backward-compat runs completed)
- [x] Provider failures fail-closed (`ConfigurationError` at startup)
- [x] No direct `genai` imports in 4 call-site files
- [x] Provenance schema (`provider`, `model`) in all trace manifests, per-file results, JSON reports, SARIF
- [x] All existing tests pass with updated mocks + new provider tests pass (83/83)
- [x] 8 fail-closed factory scenarios passing + runtime failure scenarios across 4 callers
- [x] Anthropic mode produces correct verdicts across ≥3 runs — VERIFIED/FIXED/VULNERABLE, 0 false positives
- [x] Latency delta documented — Anthropic 1.9–8.4× faster than Gemini across benchmark files
- [x] Deterministic core unchanged (obligations, verification, verdicts, enforcement)

---

## Phase 4 — UX, Frontend, and Demo Polish
**Status:** COMPLETED (2026-03-16)

### Execution status

- [x] **Step 4.1**: Created `src/core/dashboard.py` — Mission Control HTML dashboard generator. Self-contained (no external CDN), reads `argus_report.json` + trace artifacts, produces `argus_dashboard.html` with: header/provider badge, executive summary with risk level, pipeline stage timeline, per-file verdict cards (expandable, with obligation tables + action guidance + code panels), audit trail. Generated as a pipeline artifact by `cli.py --output-html`.
- [x] **Step 4.2**: Enhanced `render_mr_comment` in `src/core/reporter.py` — now includes executive summary, 4-column verdict summary table, grouped sections (Action Required → Auto-Repaired → Unverified → Verified), actionable developer guidance for VULNERABLE files with collapsible obligation details, repair diffs for FIXED files, trust model footer. All new parameters backward-compatible (optional kwargs).
- [x] **Step 4.3**: Enhanced `render_markdown_report` in `src/core/reporter.py` — now includes executive summary paragraph, risk level assessment, per-file action items, repair diffs for FIXED files, Risk Assessment section with verdict table, Recommendations section, Audit Metadata footer. All new parameters optional.
- [x] **Step 4.4**: Pipeline + CLI + GitLab adapter integration — `pipeline.run_many()` now tracks `_original_code` and `_repaired_code` dicts; `cli.py` passes them to reporter and GitLab adapter; `cli.py --output-html` wires dashboard generation non-blockingly; `gitlab_adapter.py` forwarded new `original_code`/`repaired_code` kwargs to `render_mr_comment`.
- [x] **Step 4.5**: Demo scenarios created in `demo_target/` — `safe_transfer.py` (VERIFIED), `vulnerable_transfer.py` (FIXED/VULNERABLE), `drift_withdrawal.py` (VULNERABLE), each with clear narrative docstrings. `demo_target/README.md` documents run commands and backup strategy. `demo_target/backup_artifacts/` directory created.
- [x] **Step 4.6**: Demo script written to `docs/demo-script.md` — exact 3-minute breakdown with timestamps (6 segments), narration text, screen content, key visuals, judging rubric coverage table, backup contingency plan.
- [x] **Step 4.7**: Architecture diagrams written to `docs/architecture.md` — full pipeline architecture ASCII diagram, verdict decision tree, component layer map, trust model, before/after impact comparison, quantitative evidence table.
- [x] **Step 4.8**: Tests written — `tests/test_dashboard.py` (21 tests covering generation, HTML validity, required sections, embedded data, no external deps, all verdict types, code panels, risk helpers, edge cases) + `tests/test_reporter.py` expanded (37 tests covering all 5 report formats + enhanced MR comment and Markdown report functionality). 136/136 total tests passing.
- [x] **Step 4.9**: README rewritten (`README.md`) — submission-grade 11-section document: hero positioning, what it does, custom agent/flow proof, architecture diagram, quickstart, Anthropic integration table, output artifacts table, demo scenarios, repo structure, reliability evidence, judging alignment.
- [x] **Quickstart updated**: `docs/quickstart.md` updated to reference `ANTHROPIC_API_KEY`, new dashboard artifact, and all 3 demo scenarios.

### Phase 4 evidence

- `src/core/dashboard.py` — Mission Control HTML generator
- `src/core/reporter.py` — enhanced MR comment + Markdown report
- `src/adapters/cli.py` — `--output-html` flag + dashboard integration
- `src/adapters/gitlab_adapter.py` — forwarded code dicts to render_mr_comment
- `src/core/pipeline.py` — `_original_code`/`_repaired_code` tracking
- `tests/test_dashboard.py` — 21 dashboard tests
- `tests/test_reporter.py` — 37 reporter tests (all formats + enhanced)
- `demo_target/safe_transfer.py`, `vulnerable_transfer.py`, `drift_withdrawal.py`
- `docs/demo-script.md` — 3-minute timestamped demo script
- `docs/architecture.md` — full architecture diagrams
- `README.md` — submission-grade rewrite
- `docs/quickstart.md` — updated with new artifacts and demo scenarios
- Full test suite: **136/136 passing** (`pytest tests/`)

### Phase 4 acceptance criteria status

- [x] `argus_dashboard.html` generated as a pipeline artifact, opens in any modern browser
- [x] Dashboard contains: executive summary, pipeline timeline, per-file verdict cards with expandable details, code panels, audit trail metadata
- [x] Dashboard is fully self-contained: no external CSS/JS/CDN dependencies, no network requests
- [x] MR comment includes executive summary, verdict-grouped file sections, developer action items for VULNERABLE files, repair diffs for FIXED files
- [x] MR comment renders correctly in GitLab Flavored Markdown, stays under 65,535 character limit (tested)
- [x] Markdown audit report includes executive summary, risk assessment, and recommendations
- [x] All three demo scenarios exist in `demo_target/` with expected verdicts documented
- [x] Demo script is timestamped 3-minute script with 6 segments covering full flow
- [x] Architecture diagram accurately represents current pipeline stages and trust model
- [x] README communicates product value with judging alignment table
- [x] All new and existing tests pass (136/136)
- [x] No regressions: existing JSON/SARIF/SAST report formats unchanged
- [x] CLI `--output-html` flag produces dashboard alongside all existing artifacts

---

## Phase 5 — Submission Packaging & Launch Readiness
**Status:** IN PROGRESS (engineering closure complete; external/manual submission closure pending)

### Execution status
- [x] Gate B docs created: `docs/security-posture.md`, `docs/data-handling-policy.md`
- [x] Gate C docs created: `docs/deployment-guide.md`, `docs/install-validation.md`
- [x] Gate D docs created: `docs/ops-runbook.md`, `docs/troubleshooting.md`
- [x] Gates E/F docs created: `docs/enterprise-readiness.md`, `docs/pilot-proposal.md`, `docs/competitive-positioning.md`
- [x] Gate G doc created: `docs/demo-integrity-checklist.md`
- [x] Release-hardening updates applied:
  - public pipeline API maps exposed (`original_code_map`, `repaired_code_map`)
  - CLI no longer depends on private pipeline attrs
  - GitLab SAST analyzer/scanner version metadata unified to `2.1.0`
  - hosted-mode runtime fixed (`create_llm_client(provider, model)` compatibility restored)
  - hosted-mode provider guard enforced (`anthropic` only)
  - Dockerfile no longer bakes proxy token via `ARG/ENV`
- [x] Proxy operations hardening complete:
  - `proxy/main.py` now includes `/health`, `/ready`, per-token auth, per-token usage, per-token daily limits, per-IP hourly limits, structured logging, upstream error wrapping
  - multi-token config via `ARGUS_PROXY_TOKENS_JSON` with single-token backward compatibility
  - proxy runbook added: `docs/proxy-operations.md`
- [x] LLM provider robustness improved:
  - proxy payload validation added (`text` must exist and be non-empty)
  - retry behavior retained and tested
- [x] Reliability report consolidated for Phase 5: `docs/reliability-report.md`
- [x] Large-MR stress artifacts generated:
  - `artifacts/phase5/mr-comment-stress.json` (within GitLab comment limit)
  - `artifacts/phase5/stress_dashboard.html`
- [x] Environment variable contract enumerated from source:
  - `artifacts/phase5/env-vars-contract.json`
- [x] Demo backup provenance scaffold added: `demo_target/backup_artifacts/PROVENANCE.md`
- [x] Test suite green after hosted-mode hardening: `133 passed`

### Strict remaining manual closure checklist (only items left)
1. [ ] Run 3 token-backed end-to-end demo scenarios with valid `ARGUS_PROXY_TOKEN` and archive resulting artifacts (`safe_transfer`, `vulnerable_transfer`, `drift_withdrawal`) under `demo_target/backup_artifacts/` with timestamps.
2. [ ] Capture final visual submission assets (`docs/assets/dashboard.png`, `docs/assets/mr-comment.png`, `docs/assets/terminal-run.png`, optional architecture image).
3. [ ] Record/upload final demo video and add final URLs in `docs/submission-text.md` (video URL + Devpost submission URL).
4. [ ] Manually confirm repo visibility/hackathon checklist in GitLab UI (public visibility, latest default-branch files present, no exposed secrets).

### Evidence links
- Core docs: `docs/security-posture.md`, `docs/data-handling-policy.md`, `docs/deployment-guide.md`, `docs/install-validation.md`, `docs/ops-runbook.md`, `docs/troubleshooting.md`, `docs/enterprise-readiness.md`, `docs/pilot-proposal.md`, `docs/competitive-positioning.md`, `docs/demo-integrity-checklist.md`, `docs/reliability-report.md`, `docs/proxy-operations.md`
- Hardening code: `src/core/llm_provider.py`, `src/adapters/cli.py`, `Dockerfile`, `proxy/main.py`
- Stress/validation artifacts: `artifacts/phase5/mr-comment-stress.json`, `artifacts/phase5/stress_dashboard.html`, `artifacts/phase5/env-vars-contract.json`
- Visual pack scaffold: `docs/assets/README.md`
