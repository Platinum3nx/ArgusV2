# Phase 1 Weakness Remediation Plan

## Context

Phase 1 (Core Reliability & Correctness) is marked complete, but a deep code review reveals several weaknesses that undermine the system's credibility for demo and judging. The most critical: **the "safe" benchmark file (`saturating_withdrawal.py`) always gets a `VULNERABLE` verdict**, meaning the positive half of the demo story (safe code → VERIFIED) doesn't work. This and other issues need fixing before moving to Phase 2+.

---

## Weakness Inventory

### W1 [CRITICAL]: Safe file always gets VULNERABLE

**Root cause chain:**
1. `InvariantDiscovery._query_llm()` returns `""` when `GEMINI_API_KEY` is unset → empty `assumed_inputs`
2. Even when set, LLM-produced assumptions must match the regex `variable op value` exactly to become Lean hypotheses (`_parse_assumption_to_lean` in `lean_ir_emitter.py`)
3. Without hypotheses like `(balance ≥ 0)` and `(amount ≥ 0)`, the Lean theorem `withdraw balance amount ≥ 0` is unprovable
4. Proof fails → `all_obligations_passed = False` → `compute_verdict` returns `VULNERABLE`

**Trace of the failure path:**
```
saturating_withdrawal.py
  → ObligationPolicy.derive() → non_negativity obligation (balance/amount are NUMERIC_HINT_NAMES, has_minus=True)
  → VerifierRouter.select_engine() → "lean" (no loops)
  → PythonIRLowerer.lower() → IRIfThenElse(condition=amount>balance, then=balance, else=balance-amount)
  → VerificationConditionGenerator.generate() → proposition: "(withdraw balance amount ≥ 0)"
  → LeanIREmitter.emit() → theorem with NO hypotheses (assumptions list is empty)
  → LeanVerifier.verify() → returncode != 0 (proof incomplete) → VULNERABLE
```

**Files:** `src/core/invariant_discovery.py`, `src/core/translator/lean_ir_emitter.py`, `src/core/obligation_policy.py`

### W2 [CRITICAL]: Benchmark gate doesn't test verdict correctness

The `_seeded_benchmark_gate` in `ci_integrity.py` only checks `"blocking"/"supported"/"semantic_guard_failure"` — never the actual pipeline verdict. A system that marks everything VULNERABLE passes all gates.

**File:** `src/core/ci_integrity.py`, `benchmarks/seeded/manifest.json`

### W3 [HIGH]: Mutation gate is vacuous when original is also VULNERABLE

`_evaluate_mutation` in `ci_integrity.py` (line 337) returns `VULNERABLE` for any valid translated code. If the original also returns VULNERABLE, kill rate is trivially 100%. The gate proves nothing.

**File:** `src/core/ci_integrity.py`

### W4 [HIGH]: Lean proof tactics may be insufficient

The non_negativity proof strategy in `lean_ir_emitter.py` is: `unfold; try split_ifs at *; simp_all; try linarith`. The `try` on `linarith` means it silently gives up if `linarith` alone can't close goals. Adding `omega` (integer arithmetic decision procedure) would strengthen the proof.

**File:** `src/core/translator/lean_ir_emitter.py`

### W5 [MEDIUM]: `VerificationSummary.repaired` mutated directly

`pipeline.py:321` does `summary.repaired = True`, breaking dataclass immutability expectations. Should create a new summary instead.

**File:** `src/core/pipeline.py`

### W6 [MEDIUM]: `require_docker_verify=False` undocumented gap

Phase 1 benchmarks all run with `require_docker_verify=False`. The reliability report doesn't note this. Latency numbers (~1s) may not represent production.

**File:** `scripts/phase1_reliability_run.py`, `docs/reliability-report.md`

### W7 [LOW]: Equivalence checker input sampling too narrow

`_sample_inputs` uses `randint(-6, 6)` — misses boundary values like 0, large ints, or cases where `amount > balance`.

**File:** `src/core/equivalence.py`

---

## Fix Plan

### Fix 1: Deterministic precondition derivation for non_negativity (W1 + W4)

**Approach:** Add a deterministic method to `ObligationPolicy` that derives precondition assumptions for `non_negativity` obligations based on function signatures. For any function with a `non_negativity` obligation, inject `param >= 0` for all `int` parameters that appear in arithmetic expressions. These become guaranteed Lean hypotheses regardless of LLM availability.

**Changes:**

1. **`src/core/obligation_policy.py`** — Add method `derive_preconditions(fn, obligations) -> List[AssumedInput]` that returns deterministic assumptions:
   - For each `non_negativity` obligation, find all `int` parameters of the target function
   - Generate `AssumedInput(property="param >= 0", ...)` for each
   - These are structurally valid (will pass `validate_assumptions` and `_parse_assumption_to_lean`)

2. **`src/core/pipeline.py`** — After `InvariantDiscovery.discover()`, merge deterministic preconditions with LLM-discovered assumptions (deterministic ones take priority, no duplicates)

3. **`src/core/translator/lean_ir_emitter.py`** — Add `omega` tactic after `linarith` in non_negativity proof strategy:
   ```
   unfold fn_name
   try split_ifs at *
   simp_all
   try linarith
   try omega
   ```

**Verification:** After this fix, run `saturating_withdrawal.py` through the pipeline — it should get `VERIFIED`.

### Fix 2: Add expected_verdict to benchmark gate (W2)

**Changes:**

1. **`benchmarks/seeded/manifest.json`** — Add `expected_verdict` field to each case:
   ```json
   {
     "id": "safe_saturating_withdraw",
     "path": "safe/saturating_withdrawal.py",
     "expected": "supported",
     "expected_verdict": "VERIFIED"
   },
   {
     "id": "vuln_withdraw_no_bounds",
     "path": "vulnerable/negative_withdrawal.py",
     "expected": "blocking",
     "expected_verdict": "VULNERABLE"
   }
   ```

2. **`src/core/ci_integrity.py`** — In `_seeded_benchmark_gate`, after existing checks, run the pipeline on each case and compare verdict against `expected_verdict` (when present). Fail if mismatch.

### Fix 3: Make mutation gate meaningful (W3)

**Changes:**

1. **`src/core/ci_integrity.py`** — Change `_evaluate_mutation` to return the actual verdict. Change `_mutation_gate` to compare each mutation's verdict against the original file's verdict. A mutation is "killed" only if its verdict DIFFERS from the original (or if it becomes ERROR/UNVERIFIED when original was VERIFIED/VULNERABLE).

### Fix 4: Fix VerificationSummary mutability (W5)

**Change in `src/core/pipeline.py`:** Replace `summary.repaired = True` with creating a new `VerificationSummary` with `repaired=True`, passing all other fields through.

### Fix 5: Document Docker verification gap (W6)

**Change in `docs/reliability-report.md`:** Add a "Limitations" section noting that benchmarks ran with `require_docker_verify=False` and that production latency may differ.

### Fix 6: Update Phase 1 artifacts

After all fixes:
1. Re-run `scripts/phase1_reliability_run.py` — expect `saturating_withdrawal.py` to now get VERIFIED
2. Re-run `scripts/phase1_ci_gate_check.py` — expect all gates still passing
3. Re-run `scripts/phase1_artifact_audit.py` — expect all artifacts present
4. Update `artifacts/phase1/` with new outputs
5. Update `docs/reliability-report.md` with new results
6. Update `docs/FINAL_PLAN_PROGRESS.md` to note the hardening pass

---

## Implementation Order

1. **Fix 1** (deterministic preconditions + omega tactic) — unblocks everything
2. **Fix 4** (immutability) — quick, no dependencies
3. **Fix 2** (expected_verdict in benchmark gate) — depends on Fix 1 working
4. **Fix 3** (mutation gate) — independent
5. **Fix 5** (documentation) — last
6. **Fix 6** (re-run benchmarks) — after all code changes

---

## Verification Steps

1. Run `PYTHONPATH=. python3 -m pytest tests -q` — all existing tests pass
2. Add new tests:
   - Test deterministic precondition derivation produces `balance >= 0`, `amount >= 0` for `withdraw`
   - Test that `_seeded_benchmark_gate` fails when verdict doesn't match `expected_verdict`
3. Run `PYTHONPATH=. python3 scripts/phase1_reliability_run.py` — expect `saturating_withdrawal.py` → VERIFIED
4. Run `PYTHONPATH=. python3 scripts/phase1_ci_gate_check.py` — all gates green

---

## Files to modify

| File | Change |
|------|--------|
| `src/core/obligation_policy.py` | Add `derive_preconditions()` |
| `src/core/pipeline.py` | Merge preconditions into assumptions, fix mutability |
| `src/core/translator/lean_ir_emitter.py` | Add `omega` tactic to proof strategy |
| `src/core/ci_integrity.py` | expected_verdict gate, mutation gate fix |
| `benchmarks/seeded/manifest.json` | Add `expected_verdict` fields |
| `docs/reliability-report.md` | Docker gap documentation |
| `docs/FINAL_PLAN_PROGRESS.md` | Update with hardening notes |
| `artifacts/phase1/*` | Regenerated after fixes |
| `tests/test_obligation_policy.py` | New precondition tests |
