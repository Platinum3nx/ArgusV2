# ArgusV2 Reliability Report (Phase 1)

Status: Draft scaffold (to be populated by repeated benchmark executions)

## Scope
Phase 1 reliability validation for:
- deterministic obligation derivation
- semantic guard integrity
- verifier routing correctness
- trace artifact completeness
- fail-closed behavior on unsupported/translation/runtime failures

## Environment
- Repo: ArgusV2
- Date: 2026-03-15 UTC
- Runtime note: local environment currently missing full Python test harness/toolchain execution support in this session.

## Current hardening outcomes
1. CI merge-request verification is now blocking (non-optional).
2. Loop detection in CI gates is AST-based (eliminates false positives/negatives from plain-text matching).
3. Dafny loop fallback no longer emits synthetic placeholder logic; it fails closed until deterministic lowering exists.

## Required metrics before Phase 1 sign-off
- [ ] 20+ repeated controlled runs: success rate and verdict stability.
- [ ] p95 end-to-end latency by runner profile.
- [ ] Artifact completeness rate across all verdict paths.
- [ ] Seeded benchmark corpus pass/fail matrix and drift notes.
- [ ] Mutation gate output summary with kill rate distribution.

## Evidence links
- `src/core/translator/dafny_translator.py`
- `src/core/ci_integrity.py`
- `.gitlab-ci.yml`
- `docs/FINAL_PLAN_PROGRESS.md`
