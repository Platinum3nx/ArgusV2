# ArgusV2 Architecture

## One-Line Positioning
> ArgusV2 is the trust layer for AI-accelerated software delivery: it reasons, repairs, and proves before merge.

---

## Core Trust Model

```
LLM (Claude / Gemini)          Formal Verifier (Lean 4 / Dafny)
         ↓                                    ↓
      ADVISOR                              AUTHORITY
   (generates candidates)            (proves or rejects)

Claude proposes. Lean disposes. Argus enforces.
```

The LLM proposes assumptions, translations, proof tactics, and code fixes.
The deterministic formal verifier validates every LLM output independently.
If the LLM hallucinates or fails, the pipeline fails closed — never emitting a false VERIFIED verdict.

---

## Full Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GitLab Merge Request                            │
│                    (Event Trigger Layer)                            │
│  push / MR created → argus-verify CI job fires automatically       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Argus Verified Repair Agent                       │
│                  (Autonomous — no human in loop)                    │
│                                                                     │
│  ┌───────────┐   ┌────────────┐   ┌───────────┐   ┌────────────┐  │
│  │  Discover │→  │ Translate  │→  │  Verify   │→  │  Enforce   │  │
│  │           │   │            │   │           │   │            │  │
│  │Obligations│   │Python→Lean │   │Lean 4 /   │   │MR Comment  │  │
│  │& Inputs   │   │  / Dafny   │   │  Dafny    │   │Labels      │  │
│  │(Claude)   │   │(AST + LLM) │   │(formal)   │   │Merge Gate  │  │
│  └───────────┘   └────────────┘   └─────┬─────┘   └────────────┘  │
│                                         │                          │
│                              ┌──────────┴──────────┐               │
│                              │   Obligation Fails?  │               │
│                              └──────┬──────────┬───┘               │
│                                     │          │                   │
│                              ┌──────▼────┐ ┌───▼──────────┐       │
│                              │   Proof   │ │    Secure     │       │
│                              │  Search   │ │    Repair     │       │
│                              │ (Claude)  │ │  (Claude)     │       │
│                              └──────┬────┘ └───┬──────────┘       │
│                                     │          │                   │
│                                     └─────┬────┘                  │
│                                           ▼                       │
│                                  ┌────────────────┐               │
│                                  │  Re-Verify     │               │
│                                  │ (Lean 4/Dafny) │               │
│                                  └────────────────┘               │
│                                                                     │
│    ┌──────────────────────────────────────────────────────────┐    │
│    │  TRUST MODEL: Claude = ADVISOR  |  Lean 4 = AUTHORITY   │    │
│    │  LLM proposes. Formal verifier decides. Always.         │    │
│    └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Output Artifacts                              │
│  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌──────┐ ┌─────────────────┐ │
│  │Dashboard │ │MR Comment│ │ JSON │ │SARIF │ │  Audit Traces   │ │
│  │ (HTML)   │ │(GitLab)  │ │Report│ │Report│ │  (.argus-trace) │ │
│  └──────────┘ └──────────┘ └──────┘ └──────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Verdict Decision Tree

```
                     ┌─────────────────────┐
                     │  Unsupported         │
                     │  Constructs?         │
                     └─────┬───────┬────────┘
                       YES │       │ NO
                           ▼       ▼
                      UNVERIFIED  ┌─────────────────────┐
                                  │  Translation         │
                                  │  Success?            │
                                  └─────┬───────┬────────┘
                                    NO  │       │ YES
                                        ▼       ▼
                                      ERROR   ┌─────────────────────┐
                                              │  Formal Verification │
                                              │  (Lean 4 / Dafny)   │
                                              └─────┬───────┬────────┘
                                               FAIL │       │ PASS
                                                    ▼       ▼
                                            ┌──────────┐  VERIFIED ✅
                                            │  Proof   │
                                            │  Search  │
                                            └─────┬────┘
                                             PASS │  FAIL
                                                  ▼    ▼
                                             VERIFIED ┌─────────┐
                                                       │ Repair  │
                                                       │(Claude) │
                                                       └────┬────┘
                                                       PASS │  FAIL
                                                            ▼    ▼
                                                         FIXED  VULNERABLE
                                                          🔧     🔴
```

---

## Component Layer Map

| Layer | Components | Technology |
|:---|:---|:---|
| **Event Trigger** | `.gitlab-ci.yml` argus-verify job | GitLab CI/CD |
| **Agent Identity** | `config.yml`, `.gitlab/duo/agent-config.yml` | GitLab Duo |
| **Flow Definition** | `.gitlab/duo/flows/argus_verify.yml` | GitLab Duo Flows |
| **CLI Entry** | `src/adapters/cli.py` | Python argparse |
| **Pipeline Orchestrator** | `src/core/pipeline.py` | Python |
| **Obligation Policy** | `src/core/obligation_policy.py` | Deterministic (no LLM) |
| **Invariant Discovery** | `src/core/invariant_discovery.py` | Claude via LLMClient |
| **AST Translator** | `src/core/translator/ast_translator.py` | Deterministic AST |
| **LLM Translator** | `src/core/translator/llm_translator.py` | Claude via LLMClient |
| **Dafny Translator** | `src/core/translator/dafny_translator.py` | Deterministic |
| **Lean 4 Verifier** | `src/core/verifier/lean_verifier.py` | Lean 4 (Docker) |
| **Dafny Verifier** | `src/core/verifier/dafny_verifier.py` | Dafny (Docker) |
| **Proof Search** | `src/core/proof_search.py` | Claude via LLMClient |
| **Secure Repair** | `src/core/repair.py` | Claude via LLMClient |
| **Semantic Guard** | `src/core/semantic_guard.py` | Deterministic |
| **Equivalence Check** | `src/core/equivalence.py` | Property-based |
| **Verdict Engine** | `src/core/verdict.py` | Deterministic (fail-closed) |
| **LLM Provider** | `src/core/llm_provider.py` | Anthropic SDK / google-genai |
| **Reporter** | `src/core/reporter.py` | JSON / Markdown / SARIF |
| **Dashboard** | `src/core/dashboard.py` | Self-contained HTML |
| **GitLab Adapter** | `src/adapters/gitlab_adapter.py` | python-gitlab |
| **CI Integrity** | `src/core/ci_integrity.py` | 11-gate suite |

---

## Before / After Impact

```
Without Argus                         With Argus
─────────────                         ──────────
Developer pushes code          →      Developer pushes code
Code review (manual, slow)     →      Argus auto-verifies (minutes)
Reviewer misses bounds bug     →      Obligation failure proven by Lean 4
Bug reaches production         →      Repair generated + formally verified
Security incident + rollback   →      Safe merge + full audit trail
Hours/days of toil             →      Autonomous, traceable, zero false positives
```

---

## Security and Governance Model

```
┌─────────────────────────────────────────────────────┐
│  Input: Python source code (from GitLab MR)         │
│    ↓                                                 │
│  Prompt: Code + obligations (no secrets included)   │
│    ↓                                                 │
│  LLM (Claude): Reasons over code                    │
│    ↓                                                 │
│  Formal Verifier: Independently confirms            │
│    ↓                                                 │
│  Verdict: VERIFIED / FIXED / VULNERABLE / ERROR     │
│  (deterministic — LLM output never trusted alone)  │
│    ↓                                                 │
│  Enforcement: CI gate + MR comment + labels         │
└─────────────────────────────────────────────────────┘

Fail-closed invariants:
- Missing ARGUS_PROXY_TOKEN → ConfigurationError at startup
- LLM returns empty/malformed → Pipeline fails, not VERIFIED
- Verifier timeout/error → UNVERIFIED or ERROR, never VERIFIED
- Any exception in core path → Caught, verdict = ERROR
```

---

## Quantitative Evidence (Phase 3 Validation)

| Metric | Value |
|:---|:---|
| Anthropic end-to-end runs | 9/9 (3 files × 3 runs) |
| False positives | 0 |
| Gemini backward-compat | 9/9 (same verdicts) |
| Test suite | 83/83 passing |
| Fail-closed scenarios | 14/14 tested |
| Provenance coverage | 100% (all artifacts tagged) |
| Anthropic latency advantage | 1.9–8.4× faster than Gemini |
| Verdict stability | 100% (stable across repeated runs) |
