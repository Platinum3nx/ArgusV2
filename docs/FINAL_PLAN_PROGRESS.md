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
**Status:** IMPLEMENTATION COMPLETE — Anthropic end-to-end validation pending ANTHROPIC_API_KEY

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
- [x] **Step 3.8**: Gemini backward-compat validation completed (2 runs, all files correct verdicts, provenance in all artifacts). Anthropic end-to-end validation: **pending `ANTHROPIC_API_KEY`** — run command below once key is available.

### Additional fixes applied during Phase 3 execution

- **Soundness fix**: `InvariantDiscovery._parse_assumptions()` now filters LLM assumptions with: (a) empty `property`, (b) invalid `source_type`, or (c) inter-parameter relationship constraints (e.g., `balance >= amount`). Such constraints represent business logic guards that must exist in code — accepting them as LLM assumptions caused false VERIFIED verdicts.
- **Prompt hardening**: `src/prompts/discover_invariants.md` updated with explicit schema rules, valid `source_type` values, and explicit prohibition against inter-parameter constraint invention.
- **CI gate fix**: `_seeded_benchmark_gate` now accepts FIXED when VULNERABLE is expected — FIXED means vulnerability was found AND repair succeeded, which satisfies a blocking verdict expectation.

### Anthropic validation command (run once ANTHROPIC_API_KEY is set)

```bash
export ANTHROPIC_API_KEY=<key>
python -m src.adapters.cli --file benchmarks/seeded/safe/saturating_withdrawal.py \
  --provider anthropic --allow-local-verify --output-json artifacts/phase3/anthropic_r1_safe.json \
  --output-md /dev/null --output-sarif /dev/null --output-gl-sast /dev/null --skip-gitlab-publish
python -m src.adapters.cli --file benchmarks/seeded/vulnerable/negative_withdrawal.py \
  --provider anthropic --allow-local-verify --output-json artifacts/phase3/anthropic_r1_vuln.json \
  --output-md /dev/null --output-sarif /dev/null --output-gl-sast /dev/null --skip-gitlab-publish
# Repeat above 3 times total; check artifacts/phase3/reliability-summary.json
```

### Phase 3 evidence

- `src/core/llm_provider.py` — provider contract + factory
- Diff of 4 refactored call-site files (zero `genai` references)
- `tests/test_llm_provider.py` — 8 factory tests (Anthropic + Gemini success paths + all fail-closed scenarios)
- Full test suite: `83 passed` (`pytest tests/`)
- `artifacts/phase3/reliability-summary.json` — Gemini backward-compat run evidence (2 runs, 0 false positives)
- Gemini run artifacts: `artifacts/phase3/gemini_r1_*.json`, `artifacts/phase3/gemini_r2_*.json`
- Provenance verified: `provider` + `model` in manifests, per-file results, JSON report, SARIF

### Phase 3 acceptance criteria status

- [x] `--provider anthropic` with `ANTHROPIC_API_KEY` drives full pipeline (code complete; runtime validation pending key)
- [x] Default provider is `"anthropic"` everywhere (config, CLI, docs, env var default)
- [x] `--provider gemini` with `GEMINI_API_KEY` still works (2 backward-compat runs completed)
- [x] Provider failures fail-closed (`ConfigurationError` at startup)
- [x] No direct `genai` imports in 4 call-site files
- [x] Provenance schema (`provider`, `model`) in all trace manifests, per-file results, JSON reports, SARIF
- [x] All existing tests pass with updated mocks + new provider tests pass (83/83)
- [x] 8 fail-closed factory scenarios passing + runtime failure scenarios across 4 callers
- [ ] Anthropic mode produces correct verdicts across ≥3 runs — **pending `ANTHROPIC_API_KEY`**
- [x] Latency delta documented in `artifacts/phase3/reliability-summary.json`
- [x] Deterministic core unchanged (obligations, verification, verdicts, enforcement)

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
