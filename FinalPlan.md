# FinalPlan.md — ArgusV2 Submission-Grade Execution Plan (Code Complete + Demo Ready)

## 0) Mission
Ship ArgusV2 as a **hackathon-winning, startup-grade product** that is:
- fully functional in GitLab event-driven workflows
- clearly aligned to Devpost judging and submission rules
- polished enough for a 3-minute demo video
- credible as a product engineering/security teams could pilot

This document is the single source of truth from now until submission.

---

## 1) Non-Negotiable Submission Outcomes
By submission day, ArgusV2 must satisfy all of the following:

1. **Working product flow** (trigger → verify → diagnose → repair → re-verify → MR/report output)
2. **At least one custom public agent or public flow** clearly present and demonstrated
3. **Public repository** with visible OSS license and complete setup instructions
4. **Public 3-minute demo video** showing trigger-driven autonomous action
5. **Clear text narrative** of pain, solution, and developer impact
6. **Judging-optimized evidence** for technical implementation, usability, impact, and originality

---

## 2) Product Definition (What the final product is)
ArgusV2 is a **GitLab-native autonomous DevSecOps agent platform** that protects security-critical code using:
- deterministic policy/invariant gates
- formal verification (Lean/Dafny)
- AI-powered diagnosis and repair
- fail-closed decisioning
- explainable MR and compliance artifacts

### One-line positioning
> ArgusV2 is the trust layer for AI-accelerated software delivery: it reasons, repairs, and proves before merge.

---

## 3) Hackathon Requirement Mapping (Explicit)

## 3.1 “At least one custom public agent or public flow”
ArgusV2 must explicitly satisfy and prove this requirement.

### Current assets in repo
- `.gitlab/duo/agent-config.yml` (custom Duo agent runtime config)
- `config.yml` (agent metadata)

### To make it indisputable for judges
- Ensure project is public in the GitLab AI Hackathon group
- Add README section: **“Custom Public Agent / Flow”** with file paths and run steps
- Add demo segment showing trigger-based execution by this agent/flow
- Include exact statement in Devpost submission text:
  - “ArgusV2 includes a custom public GitLab Duo agent (`Argus Verified Repair`) and demonstrates event-driven autonomous actions in GitLab CI/MR workflows.”

### Excellence criteria (beyond checkbox)
- Show the agent/flow taking real actions (not chat):
  - detect issue
  - run verification
  - produce diagnosis
  - generate patch suggestion
  - re-verify and report

## 3.2 “Chat alone won’t qualify”
ArgusV2 passes by design: all core value is event-triggered automation and CI/MR actions.

## 3.3 “Tell a story (pain → solution → outcome)”
Demo and submission must show:
- pain: security regression slips through normal process
- Argus action: autonomous verification + repair loop
- outcome: safer merge, less toil, auditable evidence

---

## 4) Judging Rubric Strategy

## 4.1 Technological Implementation
What judges need to see:
- robust codebase
- real GitLab Duo platform integration
- triggered tools/actions + reproducible outputs

Argus proof points:
- deterministic obligation policy and fail-closed contract
- IR + semantic/equivalence checks
- formal verification backends
- CI artifacts and traceability lineage

## 4.2 Design & Usability
What judges need to see:
- easy install/config
- clear outputs for developers

Argus proof points:
- fast quickstart
- readable MR summary format
- optional Mission Control UI for instant comprehension

## 4.3 Potential Impact
What judges need to see:
- solves real SDLC bottleneck
- meaningful value for teams

Argus proof points:
- pre-merge prevention of critical security regressions
- reduced security review/debug effort
- direct fit into existing GitLab workflow

## 4.4 Quality of Idea
What judges need to see:
- originality with practical use

Argus proof points:
- AI reasoning + formal proof acceptance gate
- not a generic assistant, but a trust-gated autonomous workflow

---

## 5) Anthropic Prize Positioning (without dilution)
Target: **Most Impactful on GitLab & Anthropic — Grand Prize**

### Anthropic-powered components
- Proof Diagnosis Agent (failure interpretation)
- Secure Repair Agent (patch proposal)
- Review Intelligence Agent (clear MR explanation)
- Risk Prioritization Agent (module/risk ranking)

### Deterministic core stays unchanged
- canonical policy gates
- evidence validation
- final verdict logic
- formal re-verification acceptance

### Required implementation
- Provider routing: `LLM_PROVIDER=anthropic|gemini|hybrid`
- Anthropic mode clearly documented and demoed
- provider provenance in traces and reports
- fail-closed on provider failure

### Submission message
> Anthropic provides reasoning and patch generation; Argus formal verification decides if the result is safe.

---

## 6) Final Product Architecture (Submission-grade)

## 6.1 Backend layers
1. Event ingestion (GitLab push/MR triggers)
2. Policy + invariants (trusted deterministic core)
3. Reasoning and verification (IR, VC generation, Lean/Dafny)
4. Autonomous agents (verify/diagnose/repair/risk/compliance)
5. Decision and enforcement (verdict + CI gate policy)
6. Observability and governance (traceability, metrics, audit outputs)

## 6.2 Frontend layer (Mission Control)
A lightweight but polished web UI that presents:
- pipeline timeline and stage status
- per-file verdicts and invariant health
- before/after patch and explanation
- risk score and confidence/evidence panel
- downloadable audit/compliance bundle

Goal: judges and non-technical reviewers understand value in under 45 seconds.

---

## 7) Execution Plan (Workstreams + Deliverables)

## Workstream A — Core Reliability & Correctness
### Deliverables
- stable end-to-end flow across demo benchmarks
- hardened timeout/retry/fail-closed handling
- deterministic outputs for prepared demo scenarios

### Tasks
- verify all flow transitions under normal + failure cases
- enforce artifact generation for every run path
- validate advisory vs blocking policy behavior
- cleanup and consistency across configs/prompts/model names

## Workstream B — Agent/Flow Requirement Closure
### Deliverables
- explicit custom public agent/flow documentation
- verified public visibility and reproducible setup
- demo evidence of trigger-driven autonomous actions

### Tasks
- README “Custom Public Agent / Flow” section
- quickstart command path for running flow
- submission text snippet prepared and reviewed

## Workstream C — Anthropic Integration Track
### Deliverables
- Anthropic provider integration for diagnosis/repair/review narrative
- fallback/provider governance controls
- Anthropic-mode demo run artifacts

### Tasks
- implement provider abstraction contract
- instrument provider metadata in trace outputs
- validate equivalent behavior under Anthropic mode

## Workstream D — UX & Presentation Layer
### Deliverables
- polished MR message templates
- Mission Control demo page
- clear compliance report summaries

### Tasks
- design high-signal text templates
- add visual status dashboard
- optimize readability for non-technical judges

## Workstream E — Demo Engineering
### Deliverables
- locked 3-minute script
- deterministic demo repository states
- backup recorded run + static fallback assets

### Tasks
- create baseline safe scenario
- create vulnerable scenario
- create fixed/re-verified scenario
- rehearse and time-box

## Workstream F — Startup/Commercial Packaging
### Deliverables
- enterprise readiness doc
- deployment guide + ops runbook
- pilot proposal + ROI narrative

### Tasks
- define security/data handling posture
- branch policy strategy (advisory→enforced)
- pricing/pilot framing for platform/security teams

---

## 8) Phase-by-Phase Manager Review Framework
Use this section for explicit sign-off after each phase.

## Phase 1 — Core Reliability & Correctness
### Goal
Stabilize the end-to-end autonomous pipeline so outcomes are deterministic, trustworthy, and repeatable.

### Scope
- Triggered flow execution
- Verification, diagnosis, repair, re-verification continuity
- Fail-closed behavior and artifact completeness

### Deliverables
- Reliability report
- Stable pipeline behavior across prepared benchmark scenarios
- Updated configs/prompts/model consistency

### Acceptance criteria
- End-to-end flow passes on prepared scenarios without manual intervention
- Required artifacts are produced for all major outcome paths
- Fail-closed behavior validated under error paths

### Evidence for review
- CI run links
- `docs/reliability-report.md`
- Artifact samples (`argus_report.json`, traces, MR summary output)

---

## Phase 2 — Custom Public Agent/Flow Closure
### Goal
Unambiguously satisfy and exceed the hackathon “custom public agent or flow” requirement. Judges must be able to find, understand, and verify the custom agent/flow within 60 seconds of opening the repository.

### Why this phase matters
This is a **hard gate for hackathon eligibility**. The rules state “at least one custom public agent or public flow” and “chat alone won't qualify.” Phase 1 built the working autonomous pipeline; Phase 2 makes that pipeline legible as a custom agent + flow to judges. Failing this phase = disqualification regardless of technical quality.

### Current state (entering Phase 2)
| Asset | Status | Gap |
|---|---|---|
| `.gitlab/duo/agent-config.yml` | Exists | Only defines Docker image + cache. No tools, triggers, or capabilities. |
| `config.yml` | Exists | Agent metadata only (name/desc/version). No tool or action definitions. |
| `.gitlab-ci.yml` argus-verify job | Working | Triggers on MR, runs pipeline, produces artifacts. This IS the autonomous flow — needs formal packaging. |
| `src/adapters/cli.py` | Working | CLI entry point with CI mode, artifact generation, GitLab MR publishing. |
| `src/adapters/gitlab_adapter.py` | Working | Posts MR comments, applies labels, derives verdicts. |
| `.gitlab/duo/flows/` directory | Missing | No formal Duo flow YAML definition exists. |
| README “Custom Public Agent/Flow” section | Missing | Neither README.md nor README2.md has this section. |
| `docs/quickstart.md` | Missing | No reproducible run instructions for judges. |
| `docs/custom-agent-proof.md` | Missing | No standalone proof document. |
| Submission text snippet | Not drafted | Devpost-ready statement not prepared. |

### Strategy
Claim **both** the custom agent AND public flow to be indisputable (belt and suspenders):
- **Custom Agent**: `config.yml` + enriched `.gitlab/duo/agent-config.yml` define “Argus Verified Repair” as a Duo-registered autonomous agent with declared tools and capabilities.
- **Public Flow**: `.gitlab/duo/flows/argus_verify.yml` formally defines the event-driven flow (trigger → verify → diagnose → repair → re-verify → report → MR action) that the CI pipeline executes.

### Execution steps (ordered)

#### Step 2.1 — Enrich agent configuration files
**Files**: `.gitlab/duo/agent-config.yml`, `config.yml`

`config.yml` must declare:
- `display_name`, `description`, `version` (already present)
- `tools` block listing the agent's capabilities:
  - `invariant_discovery` — extract security obligations from Python source
  - `formal_translator` — translate Python to Lean 4 / Dafny proof obligations
  - `formal_verifier` — run Lean 4 / Dafny verification and return pass/fail per obligation
  - `proof_search` — LLM-guided proof search for failing obligations
  - `secure_repair` — generate verified security patches for vulnerable code
  - `equivalence_checker` — validate translation faithfulness via property-based testing
  - `mr_publisher` — post structured verdict comments and apply labels to GitLab MRs
- `triggers` block declaring activation events:
  - `merge_request_created`
  - `merge_request_updated` (new commits pushed)
- `actions` block declaring autonomous actions the agent takes:
  - Block merge on VULNERABLE/ERROR verdicts (fail-closed)
  - Post MR comment with structured diagnosis
  - Apply `argus:verified` / `argus:vulnerable` / `argus:fixed` labels
  - Generate audit artifacts (JSON, Markdown, SARIF, GitLab SAST)

`agent-config.yml` must declare:
- Runtime image reference (already present)
- Cache paths (already present)
- Environment variable contract (`GEMINI_API_KEY`, `GITLAB_TOKEN`, `CI_*` vars)
- Resource requirements (verification engine needs)

**Acceptance**: Both files parse as valid YAML, tool/trigger/action declarations match actual codebase capabilities, no phantom features.

#### Step 2.2 — Create formal Duo flow definition
**File**: `.gitlab/duo/flows/argus_verify.yml`

Define the autonomous flow as a structured YAML document:
```
name: argus-verified-repair
description: Event-driven security verification and autonomous repair flow
trigger: merge_request (push events)
stages:
  1. discover    — extract obligations and invariants from changed Python files
  2. translate   — convert Python to formal proof language (Lean 4 / Dafny)
  3. verify      — run formal verification against obligations
  4. proof_search — (on failure) LLM-guided proof search for missing tactics
  5. repair      — (on failure) generate and re-verify secure patch
  6. report      — produce audit artifacts and structured MR comment
  7. enforce     — apply labels, block/allow merge based on verdict
```

This flow maps 1:1 to the `ArgusPipeline._run_file()` execution in `src/core/pipeline.py`. The YAML is the declarative description; the Python is the runtime implementation.

**Acceptance**: Flow YAML exists, stages match actual pipeline execution, no stages reference unimplemented functionality.

#### Step 2.3 — Write README “Custom Public Agent / Flow” section
**File**: `README.md` (rewrite or add section)

Must include:
- **Section header**: `## Custom Public Agent & Flow` (scannable in repo view)
- **Agent identity**: Name (“Argus Verified Repair”), config file paths, what it does in one sentence
- **Flow diagram**: Text-based flow showing trigger → stages → outputs
- **File path table**: Every config/flow file with its purpose, so judges can click through
- **Trigger proof**: Explain that `argus-verify` CI job activates on `$CI_MERGE_REQUEST_IID` — not manual, not chat
- **Autonomous actions taken**: List of actions the agent takes without human intervention (post comment, apply labels, block merge, generate artifacts)
- **How to run it**: 3-step quickstart (fork → push vulnerable code → observe)

**Acceptance**: A judge reading only the README can identify the custom agent name, locate its config, understand the flow, and know how to trigger it — all within 60 seconds.

#### Step 2.4 — Write quickstart documentation
**File**: `docs/quickstart.md`

Reproducible steps from zero to observed autonomous action:
1. **Prerequisites**: GitLab account, Gemini API key, Docker (for local) or GitLab Runner (for CI)
2. **Fork & configure**: Fork the repo into GitLab AI Hackathon group, set `GEMINI_API_KEY` CI variable
3. **Trigger the flow**: Create MR with a Python file containing a security-sensitive function (example provided)
4. **Observe autonomous action**: Pipeline triggers → `argus-verify` job runs → MR comment posted → labels applied → artifacts downloadable
5. **Inspect outputs**: Where to find `argus_report.json`, `Argus_Audit_Report.md`, SARIF report, trace directory

Include a “30-second local test” path:
```bash
python -m src.adapters.cli --file demo_target/vulnerable_example.py --allow-local-verify
```

**Acceptance**: A developer following only this doc can trigger and observe Argus on a fresh fork within 10 minutes.

#### Step 2.5 — Draft submission text snippet
**File**: `docs/submission-text.md`

Prepare the exact language for Devpost submission that satisfies the requirement:

> **Custom Public Agent / Flow**: ArgusV2 includes a custom public GitLab Duo agent (“Argus Verified Repair”, defined in `config.yml` and `.gitlab/duo/agent-config.yml`) and a public flow (`.gitlab/duo/flows/argus_verify.yml`) that demonstrates event-driven autonomous actions in GitLab CI/MR workflows. On every merge request, Argus autonomously: discovers security obligations, translates code to formal proof language, runs Lean 4/Dafny verification, attempts AI-powered repair when proofs fail, and posts structured verdict comments with audit artifacts — all without human intervention.

Also prepare responses to potential judge questions:
- “Is this just a CI pipeline?” → No, it's an autonomous agent with declared tools and capabilities that takes actions (MR comments, labels, merge blocking) beyond running tests.
- “Where's the agent?” → `config.yml` (agent identity), `.gitlab/duo/agent-config.yml` (runtime config), `.gitlab/duo/flows/argus_verify.yml` (flow definition).
- “Does it work without chat?” → Yes, entirely event-triggered. Chat is not involved at any point.

**Acceptance**: Submission text directly addresses the hackathon requirement with file paths judges can verify.

#### Step 2.6 — Validate public visibility
**Manual check (not code)**:
- [ ] Repository is in the GitLab AI Hackathon group and set to public
- [ ] All agent/flow config files are committed and visible in the default branch
- [ ] LICENSE file is present and visible on repo page (CC0 — already exists)
- [ ] No secrets or tokens in committed files

### Deliverables summary
| # | Deliverable | File(s) | New/Modified |
|---|---|---|---|
| 2.1 | Enriched agent configs | `config.yml`, `.gitlab/duo/agent-config.yml` | Modified |
| 2.2 | Formal flow definition | `.gitlab/duo/flows/argus_verify.yml` | New |
| 2.3 | README agent/flow proof section | `README.md` | Modified |
| 2.4 | Quickstart documentation | `docs/quickstart.md` | New |
| 2.5 | Submission text snippet | `docs/submission-text.md` | New |
| 2.6 | Public visibility validation | (manual check) | N/A |

### Acceptance criteria
- [ ] Judges can verify custom public agent/flow existence in under 1 minute from the README alone
- [ ] Agent config files declare tools, triggers, and actions that match implemented capabilities
- [ ] Flow YAML stages map 1:1 to actual `ArgusPipeline` execution
- [ ] Demo shows trigger-based autonomous actions (not chat-only)
- [ ] Quickstart is reproducible from a clean fork within 10 minutes
- [ ] Requirement is explicitly referenced in submission text with verifiable file paths
- [ ] No phantom features: every declared capability has a working code path

### Evidence for review
- Repo file paths: `.gitlab/duo/agent-config.yml`, `config.yml`, `.gitlab/duo/flows/argus_verify.yml`
- README section (visible on repo landing page)
- `docs/quickstart.md` (validated by walkthrough)
- `docs/submission-text.md` (ready for Devpost paste)
- Demo clip timestamp references showing trigger → autonomous action → output

### Risks specific to Phase 2
| Risk | Impact | Mitigation |
|---|---|---|
| GitLab Duo flow YAML schema mismatch | Judges validate against official spec, find non-conformant structure | Research current Duo flow schema before authoring; keep structure conservative |
| “Just a CI pipeline” objection | Judge scores low on originality/agent criteria | Emphasize tool declarations, MR actions (comments/labels/blocking), and agent identity beyond CI |
| README too long / buried section | Judge can't find proof in 60 seconds | Put “Custom Public Agent & Flow” section near top, use clear header, include file path table |

---

## Phase 3 — Anthropic Impact Track
### Goal
Make Anthropic Claude the primary reasoning engine for ArgusV2. Build a provider contract that is fail-closed, provenance-traced, and startup-grade — not just a wrapper swap. Default everything to Anthropic. Win the Anthropic Grand Prize.

### Why this phase matters
The Anthropic Grand Prize ("Most Impactful on GitLab & Anthropic") is the highest-value judging target. Phase 3 transforms ArgusV2 from a Gemini-coupled prototype into an Anthropic-first product. The narrative becomes: *"Claude reasons about code safety; Lean 4 proves it mathematically."* The deterministic core (obligations, verification, verdicts, enforcement) stays untouched — the LLM is the advisor, never the authority.

### Current state (entering Phase 3)
| Component | Status | Detail |
|---|---|---|
| LLM call sites | 4 sites, all Gemini-coupled | `invariant_discovery.py`, `llm_translator.py`, `proof_search.py`, `repair.py` |
| SDK | `google-genai==1.0.0` only | No Anthropic SDK in `requirements.txt` |
| API pattern | `genai.Client → .models.generate_content → response.text` | Identical `str→str` interface at all 4 sites |
| Config | `PipelineConfig.model = "gemini-2.5-pro"` | No `provider` field, no provider routing |
| CLI | `--allow-local-verify`, `--skip-gitlab-publish` | No `--provider` argument |
| Env vars | `GEMINI_API_KEY` checked at each call site | No `ANTHROPIC_API_KEY` support |
| Traces | `manifest.json` records `model` string | No `provider` field in traces or reports |
| Reports | JSON/Markdown/SARIF/SAST/MR comment | No provider attribution anywhere |
| Tests | `_FakeClient`/`_FakeModels` monkeypatching `genai.Client` | Tightly coupled to Gemini mock shape |
| Prompts | 4 active markdown files in `src/prompts/` | Provider-agnostic (plain text instructions) |

### Strategy
**Anthropic-first, Gemini-available.** Build a provider contract with explicit configuration, fail-closed enforcement, and structured provenance. One provider for all stages (no per-stage routing — that's premature complexity). Default everything to Anthropic. Keep Gemini as a secondary backend for enterprise flexibility. Demo, submission, and docs all lead with Claude.

### Architecture principle (unchanged)
```
LLM (Claude / Gemini)          Formal Verifier (Lean 4 / Dafny)
      ↓                                    ↓
   ADVISOR                              AUTHORITY
  (generates candidates)            (proves or rejects)
```
The LLM proposes assumptions, translations, proof tactics, and code fixes.
The deterministic core validates every LLM output. If the LLM hallucinates or fails, the pipeline fails closed. The verdict is never based on LLM output alone.

### Provider contract specification

#### Configuration schema and precedence
Single env var controls provider selection:
```
LLM_PROVIDER=anthropic|gemini        (default: anthropic)
```
CLI `--provider` overrides env var. `PipelineConfig.provider` overrides both.

One provider runs all 4 stages. No hybrid mode, no per-stage routing, no fallback chains. This is a deliberate constraint — the hackathon goal is to prove Anthropic drives end-to-end flows, and enterprise per-stage routing can be trivially added later because the abstraction supports it.

#### Required credentials per provider
| Provider | Required env var | Fail behavior if missing |
|---|---|---|
| `anthropic` | `ANTHROPIC_API_KEY` | `ConfigurationError` raised at pipeline startup (fail-closed) |
| `gemini` | `GEMINI_API_KEY` | `ConfigurationError` raised at pipeline startup (fail-closed) |

Credentials are validated once at `LLMClient` construction time. No silent degradation, no empty-string fallback, no deferred "check at call time" — the pipeline refuses to start without a valid key.

#### Provider stage matrix
All 4 LLM stages use the same provider. The selected provider applies uniformly:

| Stage | Implementation | LLM role | Provider |
|---|---|---|---|
| Invariant discovery | `InvariantDiscovery._query_llm()` | Extract assumptions from Python | `LLM_PROVIDER` |
| LLM translation | `LLMTranslator.translate()` | Python → Lean 4 (fallback when AST translator fails) | `LLM_PROVIDER` |
| Proof search | `ProofSearchEngine._generate_candidate()` | Repair failing Lean proofs with better tactics | `LLM_PROVIDER` |
| Secure repair | `RepairEngine._generate_fix()` | Generate fixed Python code | `LLM_PROVIDER` |

### Provenance schema
Every LLM-touching artifact emits a structured provenance block. This is not optional — provenance must appear in every trace and report artifact.

#### Schema definition
```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-6",
  "stage": "repair | discovery | translation | proof_search"
}
```

#### Where provenance appears
| Artifact | Location | Fields |
|---|---|---|
| Trace manifest (`.argus-trace/<run>/manifest.json`) | `config.provider`, `config.model` | `provider`, `model` |
| JSON report (`argus_report.json`) | Top-level `provider`, `model` | `provider`, `model` |
| MR comment | Footer line | `provider`, `model` (human-readable) |
| SARIF report | `tool.driver.properties` | `provider`, `model` |
| Per-file trace (`result.json`) | Top-level `provider` | `provider` |

### Execution steps (ordered)

#### Step 3.1 — Create `LLMClient` provider contract
**New file**: `src/core/llm_provider.py`

Define a provider contract with two concrete backends:

```python
class ConfigurationError(Exception):
    """Raised when provider is misconfigured. Pipeline must not start."""

# Protocol / base
class LLMClient:
    provider_name: str   # "anthropic" or "gemini" — recorded in provenance
    model_id: str        # "claude-sonnet-4-6" or "gemini-2.5-pro"

    def generate(self, contents: str) -> str:
        """Send prompt, return text. Raise on failure (callers handle exceptions)."""

# Concrete backends
class AnthropicClient(LLMClient):
    # Uses: anthropic.Anthropic(api_key=...).messages.create(model=..., max_tokens=..., messages=[...])
    # Returns: response.content[0].text

class GeminiClient(LLMClient):
    # Uses: genai.Client(api_key=...).models.generate_content(model=..., contents=...)
    # Returns: response.text

# Factory
def create_llm_client(provider: str, model: str | None = None) -> LLMClient:
    # provider="anthropic" → AnthropicClient, reads ANTHROPIC_API_KEY
    # provider="gemini"    → GeminiClient, reads GEMINI_API_KEY
    # Missing API key → raise ConfigurationError (fail-closed at startup)
    # Missing SDK → raise ConfigurationError (fail-closed at startup)
    # Unknown provider → raise ConfigurationError
```

Design constraints:
- The `generate()` method takes a single `contents: str` and returns `str`. No structured output, no multi-turn, no streaming. This matches all 4 existing call sites exactly.
- Credential checks happen at client construction time (once), not at every call. This eliminates the duplicated `if not api_key` checks scattered across 4 files.
- `ConfigurationError` on missing key/SDK so the pipeline fails immediately with a clear message, rather than silently producing empty results.
- `LLMClient` does not log or persist prompt contents beyond the existing trace system. Prompt data handling is governed by the provider's own retention policy (documented in Phase 5 Gate B).

**Acceptance**: `create_llm_client("anthropic")` returns a working client when `ANTHROPIC_API_KEY` is set. `create_llm_client("gemini")` returns a working client when `GEMINI_API_KEY` is set. Missing key raises `ConfigurationError`. Unknown provider raises `ConfigurationError`.

#### Step 3.2 — Extend `PipelineConfig` and CLI
**Files**: `src/core/pipeline.py`, `src/adapters/cli.py`

`PipelineConfig` changes:
```python
@dataclass
class PipelineConfig:
    provider: str = "anthropic"              # NEW — "anthropic" or "gemini"
    model: str = "claude-sonnet-4-6"         # CHANGED default from "gemini-2.5-pro"
    max_repair_attempts: int = 3
    max_proof_search_attempts: int = 3
    trace_root: str = ".argus-trace"
    allow_repair: bool = True
    allow_proof_search: bool = True
    require_docker_verify: bool = True
```

CLI changes:
- Add `--provider` argument: `choices=["anthropic", "gemini"]`, default from `LLM_PROVIDER` env var, fallback to `"anthropic"`
- Add `--model` argument: optional override, default depends on provider

`ArgusPipeline.__init__` changes:
- Create one `LLMClient` via `create_llm_client(config.provider, config.model)`
- Pass `self.llm_client` to all 4 services instead of `self.config.model`
- If `create_llm_client` raises `ConfigurationError`, pipeline startup fails with clear message

**Acceptance**: `python -m src.adapters.cli --provider anthropic` and `python -m src.adapters.cli --provider gemini` both work. Default is Anthropic. Missing key causes immediate exit with clear error, not a silent empty run.

#### Step 3.3 — Refactor 4 call sites to use `LLMClient`
**Files**: `src/core/invariant_discovery.py`, `src/core/repair.py`, `src/core/proof_search.py`, `src/core/translator/llm_translator.py`

Each file changes:

**Before** (repeated 4 times):
```python
from google import genai
# ...
api_key = os.getenv("GEMINI_API_KEY")
if not api_key: return error
if getattr(genai, "Client", None) is None: return error
client = genai.Client(api_key=api_key)
response = client.models.generate_content(model=self.model, contents=contents)
return response.text
```

**After** (repeated 4 times):
```python
from src.core.llm_provider import LLMClient
# ...
return self.llm_client.generate(contents)
```

Each class `__init__` changes from `model: str = "gemini-2.5-pro"` to `llm_client: LLMClient`.

What gets removed from each file:
- `import genai` / `SimpleNamespace` fallback
- `os.getenv("GEMINI_API_KEY")` checks
- `genai.Client` instantiation
- `getattr(genai, "Client", None)` guard

What stays identical:
- Prompt loading (`_load_prompt()`)
- Content assembly (prompt + obligations + code)
- Response parsing / validation
- Error handling (`try/except` around `self.llm_client.generate()`)

**Acceptance**: All 4 files have zero direct references to `genai`. All LLM interaction goes through `self.llm_client.generate()`.

#### Step 3.4 — Add structured provenance to traces and reports
**Files**: `src/core/pipeline.py` (`_write_manifest`, `_write_summary`), `src/core/reporter.py` (`render_json_report`, `render_mr_comment`, `render_sarif_report`)

All provenance follows the schema defined above: `{ provider, model, stage }`.

Trace manifest (`manifest.json`) — add provider fields:
```json
{
  "config": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-6",
    "max_repair_attempts": 3,
    ...
  }
}
```

Per-file trace (`result.json`) — add provider:
```json
{
  "filename": "...",
  "verdict": "VERIFIED",
  "provider": "anthropic",
  ...
}
```

JSON report (`argus_report.json`) — add top-level provider:
```json
{
  "tool": "ArgusV2",
  "provider": "anthropic",
  "model": "claude-sonnet-4-6",
  "timestamp": "...",
  ...
}
```

MR comment — add provider footer line:
```
**Provider**: Anthropic Claude Sonnet 4.6 | **Verdict**: ...
```

SARIF report — add provider to `tool.driver.properties`:
```json
"tool": {
  "driver": {
    "name": "ArgusV2",
    "properties": { "provider": "anthropic", "model": "claude-sonnet-4-6" }
  }
}
```

**Acceptance**: After a run, `grep -r "anthropic" .argus-trace/` returns hits in manifest.json and per-file result.json. `argus_report.json` contains `"provider": "anthropic"`. MR comment shows provider. SARIF report includes provider in driver properties. Provenance schema is consistent across all artifact types.

#### Step 3.5 — Add `anthropic` to dependencies
**Files**: `requirements.txt`, `Dockerfile`

`requirements.txt`:
```
anthropic>=0.40.0
google-genai==1.0.0
...
```

Dockerfile: No changes needed — `pip install -r requirements.txt` handles it. Both SDKs are installed in the image so the operator chooses at runtime via env var.

**Acceptance**: `pip install -r requirements.txt` installs both `anthropic` and `google-genai` without conflicts.

#### Step 3.6 — Update tests with fail-closed scenarios
**Files**: Modify `tests/test_repair.py`, `tests/test_llm_translator.py`. New: `tests/test_llm_provider.py`.

New test file `tests/test_llm_provider.py`:

**Factory and provider tests:**
- `test_create_anthropic_client` — factory returns `AnthropicClient` with correct `provider_name`
- `test_create_gemini_client` — factory returns `GeminiClient` with correct `provider_name`
- `test_unknown_provider_raises` — `create_llm_client("openai")` raises `ConfigurationError`
- `test_generate_returns_text` — mock client `.generate()` returns expected string

**Fail-closed scenario tests (required):**

| Test | Scenario | Expected behavior |
|---|---|---|
| `test_missing_anthropic_key` | `ANTHROPIC_API_KEY` not set, provider=anthropic | `ConfigurationError` at client construction |
| `test_missing_gemini_key` | `GEMINI_API_KEY` not set, provider=gemini | `ConfigurationError` at client construction |
| `test_empty_response` | LLM returns empty string | Caller-level handling: repair returns `(None, "empty fix")`, translator returns `TranslationOutcome(success=False)` — no false VERIFIED |
| `test_malformed_output` | LLM returns non-JSON garbage for discovery | `_parse_assumptions()` returns empty list, discovery produces zero LLM assumptions — deterministic obligations still apply |
| `test_exception_propagation` | `generate()` raises `Exception` | Callers catch and return error result — pipeline fails closed, never emits VERIFIED/FIXED |

**Existing test files:**
- Replace `_FakeClient`/`_FakeModels` monkeypatching with a simple `FakeLLMClient(LLMClient)` that returns canned text
- Test logic stays identical — only the mock target changes from `genai.Client` to the `LLMClient` passed into the constructor

**Acceptance**: Full test suite passes (`pytest tests/`). No test references `genai.Client` directly. All 5 fail-closed scenarios pass.

#### Step 3.7 — Update agent/flow configs and docs
**Files**: `config.yml`, `.gitlab/duo/agent-config.yml`, `docs/submission-text.md`

`config.yml`:
- Update `description` to mention "Anthropic Claude" as the primary reasoning engine
- Keep tools/triggers/actions unchanged (they're provider-agnostic)

`.gitlab/duo/agent-config.yml`:
- Add `ANTHROPIC_API_KEY` to `environment_contract.required` (promote from optional)
- Move `GEMINI_API_KEY` to `environment_contract.optional`
- Add `LLM_PROVIDER` to `environment_contract.optional` (default: anthropic)

`docs/submission-text.md`:
- Add Anthropic prize positioning paragraph:
  > **Anthropic Integration**: ArgusV2 uses Anthropic Claude as its primary reasoning engine for obligation discovery, code translation, proof search, and secure repair. Claude's reasoning capabilities power the intelligence layer while Lean 4 / Dafny formal verification provides the mathematical trust gate. Every Claude-generated output is validated by deterministic proof before acceptance — Claude proposes, Lean disposes.
- Update judge FAQ to include "Why Anthropic?" answer

#### Step 3.8 — Validate end-to-end Anthropic mode with quantitative thresholds
**Validation run** (manual or CI):

1. Set `ANTHROPIC_API_KEY` env var
2. Run benchmark corpus **3 or more times**: `python -m src.adapters.cli --repo-path . --mode ci --provider anthropic --allow-local-verify`
3. Verify outcomes across all runs:
   - `saturating_withdrawal.py` (safe) → VERIFIED in all runs
   - `negative_withdrawal.py` (vulnerable) → VULNERABLE in all runs
   - Verdicts match Phase 1 baseline (same deterministic core, different LLM)
4. Inspect artifacts:
   - `manifest.json` shows `"provider": "anthropic"` in every run
   - `argus_report.json` shows `"provider": "anthropic"`
   - Per-file `result.json` includes `"provider": "anthropic"`
   - Trace files contain LLM-generated content (translations, proof candidates)
5. Run same corpus with `--provider gemini` + `GEMINI_API_KEY` to confirm backward compatibility
6. Document latency delta vs Gemini baseline (one line in reliability report, not a full study)

**Quantitative acceptance thresholds:**
- Anthropic end-to-end runs: **N ≥ 3** on seeded benchmark corpus
- False VERIFIED/FIXED under provider errors: **exactly 0** (tested by Step 3.6 fail-closed scenarios)
- Verdict consistency: safe files return VERIFIED in **100%** of runs, vulnerable files return VULNERABLE in **100%** of runs
- Provenance present: `"provider"` field in **100%** of trace manifests and report artifacts

**Acceptance**: All quantitative thresholds met. Anthropic mode produces valid end-to-end results. Gemini mode still works.

### Deliverables summary
| # | Deliverable | File(s) | New/Modified |
|---|---|---|---|
| 3.1 | Provider contract + factory | `src/core/llm_provider.py` | New |
| 3.2 | Config + CLI extension | `src/core/pipeline.py`, `src/adapters/cli.py` | Modified |
| 3.3 | Call site refactor (4 files) | `invariant_discovery.py`, `repair.py`, `proof_search.py`, `llm_translator.py` | Modified |
| 3.4 | Structured provenance | `src/core/pipeline.py`, `src/core/reporter.py` | Modified |
| 3.5 | Anthropic SDK dependency | `requirements.txt` | Modified |
| 3.6 | Tests + fail-closed scenarios | `tests/test_llm_provider.py`, `tests/test_repair.py`, `tests/test_llm_translator.py` | New + Modified |
| 3.7 | Config/doc updates | `config.yml`, `agent-config.yml`, `docs/submission-text.md` | Modified |
| 3.8 | End-to-end validation | (manual/CI run) + quantitative evidence | N/A |

### Acceptance criteria
- [ ] `--provider anthropic` with `ANTHROPIC_API_KEY` drives full discover → translate → verify → proof_search → repair flow
- [ ] Default provider is `"anthropic"` everywhere (config, CLI, docs, env var default)
- [ ] `--provider gemini` with `GEMINI_API_KEY` still works (backward compatibility)
- [ ] Provider failures fail-closed (`ConfigurationError` at startup, not silent empty results)
- [ ] No direct `genai` imports remain in the 4 call-site files
- [ ] Provenance schema (`provider`, `model`) present in all trace manifests, per-file results, JSON reports, MR comments, and SARIF reports
- [ ] All existing tests pass with updated mocks + new provider tests pass
- [ ] 5 fail-closed scenarios tested and passing (missing key ×2, empty response, malformed output, exception propagation)
- [ ] Anthropic mode produces correct verdicts across **≥3 runs** on seeded benchmark corpus (VERIFIED for safe, VULNERABLE for vulnerable, **0 false positives**)
- [ ] Latency delta vs Gemini baseline documented
- [ ] Deterministic core is completely unchanged (obligations, verification, verdicts, enforcement)

### Evidence for review
- `src/core/llm_provider.py` (provider contract + factory)
- Diff of 4 refactored call-site files (zero `genai` references)
- `tests/test_llm_provider.py` results (including 5 fail-closed scenario passes)
- Full test suite pass (`pytest tests/`)
- Anthropic-mode benchmark run artifacts (≥3 runs):
  - `.argus-trace/<run>/manifest.json` with `"provider": "anthropic"`
  - Per-file `result.json` with `"provider": "anthropic"`
  - `argus_report.json` with provider attribution
- Latency observation note (in `docs/reliability-report.md` or equivalent)
- Updated `config.yml`, `agent-config.yml`, `docs/submission-text.md`

### What the deterministic core does NOT change
These files/components are explicitly out of scope for Phase 3:
- `src/core/obligation_policy.py` — deterministic preconditions
- `src/core/translator/ast_translator.py` — deterministic AST translation
- `src/core/translator/dafny_translator.py` — deterministic Dafny translation
- `src/core/verifier/lean_verifier.py` — Lean 4 formal verification
- `src/core/verifier/dafny_verifier.py` — Dafny formal verification
- `src/core/verdict.py` — verdict computation logic
- `src/core/semantic_guard.py` — semantic guard checks
- `src/core/equivalence.py` — equivalence validation
- `src/core/ci_integrity.py` — CI gate integrity suite
- `src/core/assumption_evidence.py` — assumption validation

### Security and compliance note
Prompt data handling for Phase 3 is scoped as follows:
- `LLMClient` does not log or persist prompt contents beyond the existing trace system
- No secrets (API keys, tokens) are included in outbound prompt payloads — prompts contain only code, obligations, and error messages
- Provider-specific data retention policies will be documented in Phase 5, Gate B (`docs/data-handling-policy.md`)
- Outbound prompts contain user code — operators should be aware of their provider's data processing terms

### Risks specific to Phase 3
| Risk | Impact | Mitigation |
|---|---|---|
| Anthropic SDK response format differs from expected | Parsed output breaks downstream validation | `LLMClient.generate()` normalizes to plain `str`; same parsing as before |
| Claude generates different quality output than Gemini | Benchmark verdicts differ from Phase 1 baseline | Verdicts are determined by formal verifier, not LLM quality; test both providers on benchmark corpus |
| Refactoring 4 files introduces regressions | Phase 1 reliability broken | Run full test suite after each file change; changes are mechanical (swap client, remove boilerplate) |
| Anthropic API rate limits or latency | Demo/benchmark runs fail or timeout | Set reasonable `max_tokens`; Anthropic rate limits are generous for single-pipeline usage; latency delta documented |
| Missing `anthropic` SDK in Docker image | CI runs fail | `requirements.txt` includes it; Docker rebuild picks it up |
| Provider error causes false VERIFIED | Safety gate bypass | 5 fail-closed tests explicitly verify 0 false positives under all error conditions |

---

## Phase 4 — UX, Frontend, and Demo Polish
### Goal
Make Argus instantly understandable and impressive to both technical and non-technical judges.

### Scope
- Mission Control UI or equivalent polished visual layer
- High-signal MR summary templates
- 3-minute narrative-tight demo script and assets

### Deliverables
- UI demo surface
- Final MR/report templates
- Finalized demo script + backup assets

### Acceptance criteria
- A non-technical reviewer can explain Argus value in <45 seconds
- Demo consistently runs within 3-minute judged window
- UI + MR outputs clearly communicate what broke, what was fixed, and why safe

### Evidence for review
- UI screenshots/GIF/video capture
- Final demo script with timestamps
- Example MR before/after outputs

---

## Phase 5 — Submission Packaging & Launch Readiness
### Goal
Complete all hackathon submission requirements and pass startup-grade launch gates.

### Scope
- Submission completeness (repo/license/video/description)
- Launch readiness gates A–G
- Commercial readiness docs and pilot narrative

### Deliverables
- Final submission package
- Completed gate evidence docs
- Go/No-Go checklist outcome

### Acceptance criteria
- All submission checklist items complete
- All Launch Readiness gates green with linked evidence
- Final dry run succeeds end-to-end on clean setup

### Evidence for review
- Devpost draft submission text
- Checklist completion matrix
- Gate evidence docs (`docs/*.md`) and final run logs

---

## 9) Code Completion Checklist (Submission-grade)

## Core pipeline
- [ ] Triggered execution from GitLab push/MR works reliably
- [ ] Full loop executes: verify → diagnose → repair → re-verify
- [ ] Fail-closed verdict behavior validated on all known edge paths
- [ ] Trace artifacts generated for all outcomes

## Agent/flow requirement
- [ ] `.gitlab/duo/agent-config.yml` and `config.yml` are valid and documented
- [ ] Public custom agent/flow run is demonstrated and recorded
- [ ] README includes explicit “Custom Public Agent / Flow” proof section

## Anthropic track
- [ ] Provider abstraction merged (`anthropic|gemini|hybrid`)
- [ ] Anthropic mode successfully used in demo-critical path
- [ ] Provider provenance visible in artifacts/MR summary

## UX and outputs
- [ ] MR summary is concise, actionable, and readable
- [ ] Audit report includes technical + executive summary sections
- [ ] Mission Control page works for demo and highlights value instantly

## CI and packaging
- [ ] `.gitlab-ci.yml` reflects final release workflow
- [ ] Artifact names/retention stable
- [ ] deployment quickstart works from clean environment

---

## 9) Demo Video Plan (3-minute judged format)

## Segment 1 (0:00–0:25) — Problem
Show security-critical function and why standard workflows miss this class of issue.

## Segment 2 (0:25–0:55) — Trigger
Push vulnerable commit / update MR and show Argus auto-trigger.

## Segment 3 (0:55–1:30) — Detection + Diagnosis
Show proof failure and Anthropic-powered source-level diagnosis.

## Segment 4 (1:30–2:10) — Repair + Re-verification
Show generated secure patch and successful re-check.

## Segment 5 (2:10–2:40) — Developer & Compliance UX
Show MR summary + Mission Control + exported evidence bundle.

## Segment 6 (2:40–3:00) — Close
State why this is impactful, usable, technically novel, and enterprise-ready.

---

## 10) Submission Package Checklist (Final Gate)

- [ ] Public GitLab repository in GitLab AI Hackathon group
- [ ] Visible OSS license on repo page
- [ ] Full source code + assets + run instructions
- [ ] Text description on Devpost submission
- [ ] Public YouTube/Vimeo demo video
- [ ] At least one custom public agent or public flow explicitly documented
- [ ] Judging alignment explicitly addressed in submission text
- [ ] Anthropic impact narrative included (if entering Anthropic category)

---

## 11) Deliverables to Generate Before Final Submit

## Repo/docs deliverables
- [ ] `README.md` (submission-ready rewrite)
- [ ] `docs/quickstart.md`
- [ ] `docs/deployment-guide.md`
- [ ] `docs/ops-runbook.md`
- [ ] `docs/enterprise-readiness.md`
- [ ] `docs/pilot-proposal.md`
- [ ] `docs/demo-script.md`
- [ ] `docs/custom-agent-proof.md` (or equivalent README section)

## Demo deliverables
- [ ] 3-minute final video
- [ ] fallback recording/screenshots
- [ ] architecture slide and impact slide

## Product deliverables
- [ ] Mission Control UI (demo-polished)
- [ ] final MR template output
- [ ] validated benchmark scenarios and evidence exports

---

## 12) Risk Register + Mitigations

## Risk 1: Demo flakiness (network/model/runtime)
Mitigation:
- deterministic benchmark states
- backup pre-recorded run
- local fallback assets for every critical scene

## Risk 2: Requirement ambiguity (custom agent/flow)
Mitigation:
- explicit public proof section with file paths and run commands
- direct mention in submission text and video narration

## Risk 3: Too technical / low usability score
Mitigation:
- Mission Control visual layer
- plain-English MR summaries
- executive summary in reports

## Risk 4: Scope overload
Mitigation:
- prioritize narrative-critical features first
- sequence high-ambition features with demo impact lens

## Risk 5: Anthropic integration instability
Mitigation:
- provider abstraction + fallback mode
- fail-closed behavior on provider errors

---

## 13) Definition of Done (True Submission Grade)
ArgusV2 is submission-grade only when all are true:

1. **Autonomous and triggered** (not chat-only)
2. **Proof-gated and fail-closed** (trusted outcomes)
3. **Readable and usable** (developer + judge comprehension)
4. **Public requirement-compliant** (agent/flow + repo + video + docs)
5. **Commercially credible** (deployment + governance + pilot narrative)

---

## 14) Launch Readiness Addendum (Startup-Grade Certification Gates)
This section converts ambition into objective pass/fail criteria. ArgusV2 is **not** considered startup-grade until every gate below is green.

## 14.1 Gate A — Production Reliability
### Required checks
- [ ] End-to-end pipeline success rate >= 95% on controlled benchmark corpus across 20+ repeated runs
- [ ] p95 full-run latency documented and within target budget (define target per runner profile)
- [ ] Deterministic verdict stability across repeated identical runs (no unexplained drift)
- [ ] Retry and timeout behavior verified for verifier and LLM-provider failures

### Evidence artifacts
- `docs/reliability-report.md`
- benchmark replay logs + summarized metrics table

## 14.2 Gate B — Security, Privacy, and Governance
### Required checks
- [ ] Secret handling model documented (token scopes, storage location, rotation policy)
- [ ] Trace/prompt data policy documented (retention window, redaction strategy, export controls)
- [ ] Role model documented (developer/devops/security/admin permissions)
- [ ] Fail-closed behavior validated under provider/runtime failures

### Evidence artifacts
- `docs/security-posture.md`
- `docs/data-handling-policy.md`

## 14.3 Gate C — Deployability & Environment Compatibility
### Required checks
- [ ] Fresh install validated from clean environment using docs only
- [ ] Runner compatibility matrix tested (at least 2 realistic runner environments)
- [ ] Upgrade/versioning strategy documented (config and image version handling)
- [ ] Environment variable contract frozen and validated

### Evidence artifacts
- `docs/install-validation.md`
- `docs/compatibility-matrix.md`

## 14.4 Gate D — Operability & Supportability
### Required checks
- [ ] Monitoring points defined (pipeline outcomes, provider errors, verifier errors, latency)
- [ ] Incident runbooks exist for top failure modes
- [ ] Troubleshooting guide maps symptoms to fixes
- [ ] Minimal support SLA assumptions documented for pilot customers

### Evidence artifacts
- `docs/ops-monitoring.md`
- `docs/incident-runbook.md`
- `docs/troubleshooting.md`

## 14.5 Gate E — Product UX Quality (Frontend + Developer Experience)
### Required checks
- [ ] Mission Control UI communicates status/value clearly to non-technical viewers
- [ ] MR summaries are actionable and consistently understandable
- [ ] Core UX path tested with at least 3 users (or equivalent review) and feedback incorporated
- [ ] UI + report outputs avoid ambiguous verdict language

### Evidence artifacts
- `docs/ux-validation.md`
- screenshot/GIF pack used in submission and sales deck

## 14.6 Gate F — Commercial Readiness
### Required checks
- [ ] ICP and buyer persona defined (platform/security engineering leaders)
- [ ] 30-day pilot plan with success metrics defined
- [ ] ROI narrative tied to measurable outcomes (time saved, regressions reduced)
- [ ] Competitive positioning one-pager completed

### Evidence artifacts
- `docs/commercial-readiness.md`
- `docs/pilot-success-metrics.md`
- `docs/competitive-positioning.md`

## 14.7 Gate G — Demo Integrity (No Demo-Only Shortcuts)
### Required checks
- [ ] Demo path uses the same production code path and configuration profile (no hardcoded bypasses)
- [ ] Any seeded demo fixtures are explicitly labeled and reproducible
- [ ] No hidden/manual intervention required during demo flow
- [ ] Backup demo assets represent real runs from the same build/version

### Evidence artifacts
- `docs/demo-integrity-checklist.md`
- reproducibility commands and commit hashes

## 14.8 Final Go/No-Go Rule
ArgusV2 is approved as “startup-grade + submission-grade” only when:
- [ ] All submission checklist items are complete
- [ ] All Launch Readiness gates A–G are green with evidence docs linked
- [ ] Final dry run (install → execute → observe → explain) succeeds end-to-end without manual patching

---

## 15) Final Strategic Guidance
To maximize both judging and market potential, present ArgusV2 as:

> A GitLab-native autonomous security teammate that uses Anthropic reasoning and formal proof gates to prevent security regressions before merge.

Build and narrate around outcomes:
- safer merges
- faster reviews
- auditable trust
- practical path to enterprise adoption
