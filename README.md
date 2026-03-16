# ArgusV2 — The Trust Layer for AI-Accelerated Software Delivery

> **Claude proposes. Lean disposes. Argus enforces.**

ArgusV2 is a **GitLab-native autonomous DevSecOps agent** that prevents security regressions before merge using Anthropic Claude for reasoning and Lean 4 / Dafny for mathematical formal verification. It is event-triggered, fail-closed, and enterprise-ready.

```
Trigger → Discover → Translate → Verify → [Proof Search] → [Repair] → Re-verify → Enforce
```

---

## What It Does

A developer pushes a Python function without a bounds check. ArgusV2 triggers automatically:

1. **Discovers** security obligations from the source code (Claude)
2. **Translates** the function into Lean 4 proof obligations (AST + Claude)
3. **Verifies** the obligations formally (Lean 4 / Dafny — the mathematical authority)
4. **Diagnoses** failures and searches for proof repairs (Claude)
5. **Generates** a verified security patch and re-proves it (Claude → Lean 4)
6. **Reports** structured outputs: MR comment, dashboard, SARIF, JSON trace artifacts
7. **Enforces** the verdict: blocks VULNERABLE merges, applies labels, posts evidence

**Claude is the advisor. Lean 4 is the authority. The verdict is mathematical, not heuristic.**

---

## Custom Public Agent & Flow (Judge 60-second check)

ArgusV2 satisfies the GitLab hackathon "custom public agent or public flow" requirement:

| Asset | File | Purpose |
|:---|:---|:---|
| Custom agent identity | `config.yml` | Name, capabilities, tools, triggers, actions |
| Agent runtime config | `.gitlab/duo/agent-config.yml` | Docker image, env contract, capabilities |
| Public flow definition | `.gitlab/duo/flows/argus_verify.yml` | Declarative 7-stage autonomous flow |
| CI event trigger | `.gitlab-ci.yml` | Fires `argus-verify` on `$CI_MERGE_REQUEST_IID` |
| Quickstart | `docs/quickstart.md` | Fork-to-action in 10 minutes |

**Agent name**: `Argus Verified Repair`
**Trigger**: Every merge request push event (not chat)
**Autonomous actions**: MR comment · labels (`argus:verified`, `argus:fixed`, `argus:vulnerable`) · merge gate · artifact generation

---

## How It Works

```
┌────────────────────────────────────────────────────────┐
│              GitLab Merge Request                      │
│        (push → argus-verify job fires)                 │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│           Argus Verified Repair (Autonomous)           │
│                                                        │
│  Discover → Translate → Verify ──► [Proof Search]     │
│    (Claude)   (AST+LLM)  (Lean 4)      (Claude)       │
│                              │                         │
│                         FAIL ▼                         │
│                       [Repair] → Re-verify             │
│                       (Claude)   (Lean 4)              │
│                                                        │
│  TRUST MODEL: Claude = ADVISOR | Lean 4 = AUTHORITY   │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│                  Output Artifacts                      │
│  Dashboard (HTML) · MR Comment · JSON · SARIF · Trace │
└────────────────────────────────────────────────────────┘
```

---

## Quick Start

**30-second local test** (no GitLab needed):

```bash
# 1. Clone and install
git clone <repo-url> && cd ArgusV2
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY=<your-key>

# 3. Audit a vulnerable file
python -m src.adapters.cli \
  --file demo_target/vulnerable_transfer.py \
  --allow-local-verify \
  --provider anthropic

# 4. Open the dashboard
open argus_dashboard.html   # macOS
# or: xdg-open argus_dashboard.html  (Linux)
```

**Full CI trigger** (in your GitLab fork):

```bash
# 1. Fork into GitLab AI Hackathon group
# 2. Set CI/CD variables: ANTHROPIC_API_KEY, GITLAB_TOKEN
# 3. Push a Python file change → MR auto-triggers argus-verify
```

See [`docs/quickstart.md`](docs/quickstart.md) for the complete walkthrough.

---

## Anthropic Integration

ArgusV2 uses **Anthropic Claude** (`claude-sonnet-4-6`) as its primary reasoning engine across all four LLM stages:

| Stage | Claude's Role | What Lean 4 Does |
|:---|:---|:---|
| Invariant Discovery | Extracts security obligations from Python | — |
| Lean Translation | Translates obligations to formal proof code | Verifies the translation |
| Proof Search | Generates repaired proof tactics | Confirms the proof holds |
| Secure Repair | Generates a fixed Python implementation | Re-verifies the fix |

**Key design principle**: Claude proposes — Lean disposes. Every Claude output is validated by the formal verifier. False positives (false VERIFIED verdicts) are impossible by construction.

**Provider options**: `--provider anthropic` (default) or `--provider gemini`

**Fail-closed**: Missing `ANTHROPIC_API_KEY` → `ConfigurationError` at startup. No silent degradation.

**Provenance**: Every trace artifact records `provider` and `model` for full auditability.

---

## Output Artifacts

Every run produces:

| Artifact | Path | Purpose |
|:---|:---|:---|
| Mission Control Dashboard | `argus_dashboard.html` | Self-contained visual overview — open in any browser |
| JSON Report | `argus_report.json` | Machine-readable verdicts, obligations, assumptions |
| Audit Report | `Argus_Audit_Report.md` | Human-readable executive summary + risk assessment |
| SARIF Report | `argus-sarif-report.json` | Standard SARIF 2.1.0 for security tooling integration |
| GitLab SAST | `gl-sast-report.json` | GitLab Security Dashboard integration |
| CI Gates | `argus-ci-gates.json` | 11-gate integrity suite results |
| Trace Directory | `.argus-trace/<run>/` | Full per-file audit trail with Lean proofs + repair code |

---

## Demo Scenarios

Three pre-built scenarios in `demo_target/`:

| File | Expected Verdict | Narrative |
|:---|:---|:---|
| `safe_transfer.py` | VERIFIED | "Already safe — Argus confirms mathematically." |
| `vulnerable_transfer.py` | FIXED | "Missing bounds check — Argus catches and repairs it." |
| `drift_withdrawal.py` | VULNERABLE | "Looks safe — formal proof exposes the hidden flaw." |

---

## Repository Structure

```
├── .gitlab/
│   ├── duo/
│   │   ├── agent-config.yml         # Agent runtime: image, env contract, capabilities
│   │   └── flows/
│   │       └── argus_verify.yml     # Public 7-stage autonomous flow definition
│   └── .gitlab-ci.yml              # CI event trigger (MR → argus-verify job)
├── src/
│   ├── adapters/
│   │   ├── cli.py                   # CLI entrypoint — all modes and output artifacts
│   │   └── gitlab_adapter.py        # MR comment, label, and merge gate publishing
│   ├── core/
│   │   ├── pipeline.py              # ArgusPipeline orchestrator
│   │   ├── dashboard.py             # Mission Control HTML generator (Phase 4)
│   │   ├── reporter.py              # JSON / Markdown / SARIF / MR comment renderers
│   │   ├── llm_provider.py          # Provider contract (Anthropic/Gemini abstraction)
│   │   ├── obligation_policy.py     # Deterministic obligation derivation
│   │   ├── invariant_discovery.py   # Claude-powered obligation discovery
│   │   ├── proof_search.py          # Claude-powered Lean proof repair
│   │   ├── repair.py                # Claude-powered secure code repair
│   │   ├── translator/              # AST, LLM, and Dafny translators
│   │   ├── verifier/                # Lean 4 and Dafny verifier backends
│   │   ├── verdict.py               # Fail-closed verdict computation
│   │   └── ci_integrity.py          # 11-gate CI integrity suite
│   └── utils/
├── tests/                           # 136 tests, 100% passing
├── benchmarks/seeded/               # Deterministic benchmark corpus (3 scenarios)
├── demo_target/                     # Demo scenarios with pre-generated backup artifacts
├── docs/
│   ├── quickstart.md                # Fork-to-action walkthrough
│   ├── submission-text.md           # Devpost requirement language + judge FAQ
│   ├── demo-script.md               # 3-minute demo script with timestamps
│   ├── architecture.md              # Full architecture diagrams
│   └── reliability-report.md        # Phase 1 reliability evidence
├── config.yml                       # Public agent identity, tools, triggers, actions
├── Dockerfile
└── requirements.txt
```

---

## Reliability Evidence

| Metric | Value |
|:---|:---|
| Test suite | **136/136 passing** |
| Anthropic end-to-end validation runs | **9/9** (3 files × 3 runs) |
| False positives | **0** |
| Verdict stability | **100%** (same result across repeated runs) |
| Gemini backward-compat | **9/9** (same verdicts) |
| Fail-closed scenarios tested | **14/14** |
| Anthropic latency advantage | **1.9–8.4× faster** than Gemini baseline |

---

## Judging Alignment

| Judging Category | ArgusV2 Evidence |
|:---|:---|
| Technological Implementation | Lean 4/Dafny formal verification, Claude reasoning, 11-gate CI integrity suite, deterministic obligation policy, trace artifacts |
| Design & Usability | Mission Control dashboard (45-second comprehension), enhanced MR comments with repair diffs, executive summary reports |
| Potential Impact | Pre-merge prevention of critical security regressions; autonomy removes security review toil; enterprise audit trail |
| Quality of Idea | AI reasoning + formal proof acceptance gate — not a generic assistant but a trust-gated autonomous workflow |
| Custom Public Agent/Flow | `config.yml` + `agent-config.yml` + `argus_verify.yml` — indisputable by design |
| Anthropic Grand Prize | Claude drives all 4 reasoning stages with full provenance; 1.9–8.4× latency advantage; fail-closed on provider errors |

---

## License

CC0 — Public Domain. See `LICENSE`.

---

_ArgusV2 — Autonomous DevSecOps · Claude proposes · Lean disposes · Argus enforces_
