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
Make Argus instantly understandable and impressive to both technical and non-technical judges. Build a visual layer that communicates the full verification story (trigger → discover → verify → repair → prove → enforce) in under 45 seconds. Upgrade MR comments from functional tables into actionable developer summaries. Lock a 3-minute demo script that is rehearsable, deterministic, and narrative-tight.

### Why this phase matters
Phases 1-3 built a technically rigorous product — deterministic verification, fail-closed verdicts, provider-traced artifacts, and end-to-end Anthropic integration. But hackathon judges allocate **at most 3 minutes** to each submission. If they can't instantly grasp what Argus does, why it matters, and see it working, the technical depth is invisible. Phase 4 converts engineering quality into perceived quality. It is also the transition point from "hackathon project" to "startup-grade product" — enterprise buyers and pilot customers evaluate tools on developer experience and visual clarity, not just correctness.

Additionally, the judging rubric explicitly scores **"Design & Usability"** as one of four categories. Phase 4 directly targets this rubric dimension while reinforcing the others (demo script reinforces "Technological Implementation" and "Potential Impact"; Mission Control reinforces "Quality of Idea").

### Current state (entering Phase 4)
| Component | Status | Gap |
|---|---|---|
| MR comment template (`render_mr_comment`) | Working | Minimal — table of files + verdicts + provider footer. No executive summary, no developer action items, no before/after diffs, no obligation detail. |
| Markdown report (`render_markdown_report`) | Working | Lists files with verdicts and obligations. No executive summary, no risk assessment, no recommendation section. |
| JSON report (`render_json_report`) | Working | Machine-readable, complete. Used as data source for dashboard. |
| SARIF report (`render_sarif_report`) | Working | Standard SARIF 2.1.0 for GitLab Security Dashboard integration. |
| GitLab SAST report (`render_gitlab_sast_report`) | Working | Standard GitLab SAST format. Adequate. |
| Legacy frontend | Exists (`legacy/frontend/`) | Next.js 16 + React 19 + Tailwind 4 + Framer Motion. Has components (FileResultCard, ProofViewer, StatusBanner, ThinkingProcess). But: calls non-existent streaming API endpoints (`/audit`, `/audit_repo`), references Gemini, uses old schema (verified/failed/patched), not integrated with current pipeline. |
| Mission Control / HTML dashboard | Missing | No standalone visual dashboard exists. |
| Demo script | Missing | Section 9 of this doc has a rough outline but no timestamped script, narration text, or screen-by-screen breakdown. |
| Demo target scenarios | Missing | `demo_target/` directory is empty. Benchmark scenarios exist in `benchmarks/seeded/` but no demo-specific scenarios with narrative context. |
| Architecture diagram | Missing | No visual architecture diagram for demo/docs. |
| CLI dashboard output | Not implemented | CLI produces JSON/Markdown/SARIF/SAST but no HTML dashboard artifact. |

### Strategy
**Artifact-first dashboard, enhanced reporter, locked demo.** Three parallel tracks:

1. **Mission Control Dashboard** — Build a self-contained HTML report generator (`src/core/dashboard.py`) that reads pipeline trace artifacts and produces a single `argus_dashboard.html` file. No server required — the HTML file is a CI artifact that judges can open in any browser. This avoids the complexity of maintaining a separate frontend server while delivering full visual impact. The dashboard must be impressive enough for demo video screenshots and clear enough for non-technical comprehension.

2. **Enhanced MR/Report Templates** — Upgrade `render_mr_comment` to include executive summary, developer action items, obligation details, and before/after code diffs for FIXED files. Upgrade `render_markdown_report` with executive summary and risk assessment. Keep changes backward-compatible with existing GitLab adapter.

3. **Demo Engineering** — Create a precise 3-minute demo script with timestamped beats, narration text, and screen content. Prepare deterministic demo scenarios in `demo_target/` with clear narrative context. Pre-generate backup artifacts for offline fallback.

### Architecture principle
```
Pipeline run → Trace artifacts (JSON)
                     ↓
              Dashboard generator
                     ↓
         argus_dashboard.html (self-contained)
              - Embedded CSS/JS
              - No external dependencies
              - Reads from argus_report.json + trace manifests
              - Verdict timeline + per-file cards + code diffs
```

The dashboard is generated **after** the pipeline run, not during it. It reads the same artifacts that CI integrity gates validate, ensuring what the judge sees is what the pipeline actually produced. No separate data path, no demo-only shortcuts.

### Execution steps (ordered)

#### Step 4.1 — Mission Control HTML Dashboard Generator
**New file**: `src/core/dashboard.py`

Build a Python module that generates a self-contained HTML dashboard from pipeline output artifacts. The dashboard is a single `.html` file with embedded CSS and JavaScript — no external CDN links, no server, no build step. Judges open it in a browser and instantly understand what Argus did.

**Input data sources:**
- `argus_report.json` — summary + per-file verdicts, obligations, assumptions
- `.argus-trace/<run>/manifest.json` — run metadata (provider, model, config)
- `.argus-trace/<run>/summary.json` — aggregated results
- `.argus-trace/<run>/files/<filename>/result.json` — per-file details
- `.argus-trace/<run>/files/<filename>/02_translation.lean` — Lean 4 proof code (when available)
- `.argus-trace/<run>/files/<filename>/04_repair_0.py` — repaired Python code (when available)

**Dashboard sections (top to bottom):**

1. **Header bar** — "Argus Mission Control" branding, run timestamp, provider badge (Anthropic Claude / Gemini), overall verdict status indicator (green/yellow/red).

2. **Executive summary panel** — One-sentence outcome: "Argus audited N files. M verified, K repaired, J require attention." Risk level badge (CLEAR / ATTENTION / CRITICAL). This is the "45-second comprehension" target.

3. **Pipeline timeline** — Horizontal stage visualization showing: Trigger → Discover → Translate → Verify → [Proof Search] → [Repair] → [Re-verify] → Enforce. Each stage shows status (completed/skipped/failed) and timing if available. This communicates the autonomous multi-stage flow at a glance.

4. **Per-file verdict cards** — Expandable cards for each audited file:
   - File name + verdict badge (VERIFIED green, FIXED yellow, VULNERABLE red, UNVERIFIED orange, ERROR gray)
   - Obligation list with pass/fail indicators
   - Assumption list with source attribution
   - Engine used (Lean 4 / Dafny)
   - Message / finding description
   - **Code panel** (expandable): Side-by-side original Python + Lean 4 proof / repaired code

5. **Audit trail panel** — Provider attribution, trace directory path, artifact checksums, run configuration. This proves the dashboard represents a real run, not a mock.

6. **Footer** — "Generated by ArgusV2 — Autonomous DevSecOps Agent" + version + timestamp.

**Visual design principles:**
- Dark theme (matches the legacy frontend aesthetic, looks professional on video)
- Color coding: green (#10B981) for VERIFIED, amber (#F59E0B) for FIXED, red (#EF4444) for VULNERABLE, orange (#F97316) for UNVERIFIED, gray (#6B7280) for ERROR
- Monospace font for code blocks, sans-serif for text
- Smooth CSS transitions for expandable sections (no JS framework required — use `<details>`/`<summary>` with CSS or minimal vanilla JS)
- Responsive layout (works in demo video and on judge's laptop)

**Implementation approach:**
```python
def generate_dashboard(
    report_path: str,           # Path to argus_report.json
    trace_root: str = ".argus-trace",
    run_id: str | None = None,  # Auto-detect latest if None
    output_path: str = "argus_dashboard.html",
) -> str:
    """Generate self-contained HTML dashboard. Returns output path."""
```

The function:
1. Reads `argus_report.json` and trace artifacts
2. Collects Lean 4 proof code and repaired Python code from trace files
3. Renders all data into a single HTML template with inline CSS and JS
4. Writes to `output_path`

HTML template structure:
- All CSS is in a `<style>` block (no external stylesheets)
- All JS is in a `<script>` block (vanilla JS, no frameworks)
- Data is embedded as a `<script type="application/json" id="argus-data">` block
- JS reads the embedded data and renders the interactive elements
- Total file size target: < 200KB (text-heavy, no images)

**Acceptance**: `generate_dashboard("argus_report.json")` produces a valid HTML file that opens in Chrome/Firefox/Safari, displays all verdict information, and communicates the Argus value proposition to a non-technical viewer within 45 seconds. No external dependencies or network requests.

#### Step 4.2 — Enhanced MR Comment Template
**File**: `src/core/reporter.py` (modify `render_mr_comment`)

Transform the MR comment from a minimal table into a high-signal developer summary. The comment is the primary interface between Argus and the developer — it must be immediately actionable.

**Current format:**
```markdown
## Argus Formal Verification Report

**Files Audited**: 3 | Verified: 1 | Fixed: 1 | Vulnerable: 1 | Unverified/Error: 0

| File | Verdict | Finding |
|:---|:---|:---|
| `safe.py` | VERIFIED | n/a |
| `vuln.py` | FIXED | Repaired and verified |
| `drift.py` | VULNERABLE | Obligation failed: non_negative_result |

**Reasoning Provider**: Anthropic claude-sonnet-4-6 | **Verification Engine**: Lean 4 / Dafny
```

**New format:**
```markdown
## Argus Formal Verification Report

### Executive Summary
Argus audited **3 files** in this merge request. **1 vulnerability was detected and automatically repaired**. 1 file requires developer attention.

| Status | Count |
|:---|:---|
| Verified (safe to merge) | 1 |
| Fixed (auto-repaired, verified) | 1 |
| Vulnerable (action required) | 1 |

---

### Action Required

**`drift.py`** — VULNERABLE
> **What failed**: Obligation `non_negative_result` — the function can return a negative value when `amount > balance`.
> **What this means**: An attacker could trigger a negative balance, leading to unauthorized fund creation.
> **What to do**: Add a bounds check before the subtraction, or clamp the result to zero.

<details>
<summary>Obligation details (1 failed)</summary>

| Obligation | Status | Description |
|:---|:---|:---|
| `non_negative_result` | FAILED | Function result must be >= 0 |

</details>

---

### Auto-Repaired

**`vuln.py`** — FIXED
> Argus detected a missing bounds check and generated a verified repair.

<details>
<summary>View repair diff</summary>

```diff
- def withdraw(balance: int, amount: int) -> int:
-     return balance - amount
+ def withdraw(balance: int, amount: int) -> int:
+     if amount > balance:
+         return balance
+     return balance - amount
```

</details>

---

### Verified

**`safe.py`** — VERIFIED
> All 2 obligations passed formal verification.

---

**Reasoning**: Anthropic Claude Sonnet 4.6 | **Verification**: Lean 4 / Dafny | **Trace**: `.argus-trace/<run_id>`
```

**Key changes to `render_mr_comment`:**
1. Add executive summary paragraph with counts and one-line outcome
2. Group files by verdict category (Action Required → Auto-Repaired → Verified) instead of flat table
3. For VULNERABLE files: explain what failed, what it means, and what to do
4. For FIXED files: show the repair diff in a collapsible `<details>` block
5. For VERIFIED files: confirm obligation count and engine
6. Use collapsible `<details>` blocks for obligation details (keeps comment scannable)
7. Preserve provider attribution footer

**Function signature change:**
```python
def render_mr_comment(
    files: List[FileReport],
    provider: str = "",
    model: str = "",
    repaired_code: Dict[str, str] | None = None,  # NEW: filename → repaired code
    original_code: Dict[str, str] | None = None,   # NEW: filename → original code
) -> str:
```

The `repaired_code` and `original_code` dicts are optional — when provided, the comment includes repair diffs. When not provided (backward-compatible), the comment omits diffs.

**Acceptance**: MR comment includes executive summary, grouped verdict sections, actionable developer guidance for VULNERABLE files, and repair diffs for FIXED files. Comment renders correctly in GitLab Flavored Markdown. Total comment length stays under 65,535 characters (GitLab note body limit).

#### Step 4.3 — Enhanced Markdown Audit Report
**File**: `src/core/reporter.py` (modify `render_markdown_report`)

Upgrade the standalone Markdown report (`Argus_Audit_Report.md`) from a flat table to a structured audit document suitable for compliance review and demo screenshots.

**New structure:**
1. **Title + metadata** — Report title, timestamp, provider, run ID
2. **Executive summary** — One-paragraph outcome with risk level
3. **Verdict summary table** — Same as current, but with color-coded status column
4. **Per-file detailed analysis** — For each file:
   - Verdict badge + engine + message
   - Obligations table with pass/fail per obligation
   - Assumptions list with source attribution and evidence IDs
   - For FIXED files: original vs repaired code blocks
5. **Risk assessment** — Aggregate risk level based on verdict distribution and obligation severity
6. **Recommendations** — Actionable next steps grouped by priority
7. **Audit metadata** — Provider, model, trace path, artifact hashes

**Function signature change:**
```python
def render_markdown_report(
    files: List[FileReport],
    provider: str = "",
    model: str = "",
    repaired_code: Dict[str, str] | None = None,
    original_code: Dict[str, str] | None = None,
) -> str:
```

**Acceptance**: Report is a valid Markdown document that renders cleanly in GitLab/GitHub preview. Contains executive summary, risk assessment, and actionable recommendations.

#### Step 4.4 — Pipeline integration for enhanced reports
**Files**: `src/core/pipeline.py` (modify `run_many`), `src/adapters/cli.py` (modify `main`)

Wire the enhanced reporter functions and dashboard generator into the existing pipeline flow.

**Pipeline changes (`run_many`):**
Currently `run_many` returns `List[FileReport]`. It needs to additionally track original and repaired code so reporters can generate diffs:

```python
@dataclass
class BatchResult:
    reports: List[FileReport]
    original_code: Dict[str, str]      # filename → original Python
    repaired_code: Dict[str, str]      # filename → repaired Python (FIXED only)
```

Change `run_many` to return `BatchResult` (or add code tracking attributes). This keeps the data flow clean — the pipeline already has this information in `PipelineResult.repaired_code`, it just needs to surface it.

**CLI changes:**
- Add `--output-html` argument: `type=str, default="argus_dashboard.html"` — path for dashboard output
- After generating JSON/Markdown/SARIF/SAST, call `generate_dashboard()` with the report JSON and trace root
- Pass `original_code` and `repaired_code` dicts to `render_mr_comment` and `render_markdown_report`
- Dashboard generation is non-blocking — if it fails, the pipeline still produces all other artifacts

**GitLab adapter changes (`build_comment`):**
- Pass `original_code` and `repaired_code` through to `render_mr_comment` so MR comments include diffs

**Acceptance**: Running `python -m src.adapters.cli --mode ci --allow-local-verify` produces all existing artifacts (JSON, Markdown, SARIF, SAST) plus `argus_dashboard.html`. MR comments include enhanced formatting when published to GitLab.

#### Step 4.5 — Demo scenario preparation
**Directory**: `demo_target/`

Create three demo scenarios that tell a compelling narrative story. These are distinct from the `benchmarks/seeded/` corpus (which is for automated testing). Demo scenarios are designed for human comprehension — they have meaningful variable names, realistic function signatures, and clear security implications.

**Scenario 1: Safe function** (`demo_target/safe_transfer.py`)
```python
def transfer(sender_balance: int, amount: int) -> int:
    """Transfer funds with proper bounds checking."""
    if amount <= 0:
        return sender_balance
    if amount > sender_balance:
        return sender_balance
    return sender_balance - amount
```
- Expected verdict: VERIFIED
- Narrative: "This function is already safe. Argus confirms it mathematically."

**Scenario 2: Vulnerable function** (`demo_target/vulnerable_transfer.py`)
```python
def transfer(sender_balance: int, amount: int) -> int:
    """Transfer funds — missing bounds check!"""
    return sender_balance - amount
```
- Expected verdict: FIXED (repair succeeds) or VULNERABLE (if repair fails)
- Narrative: "A developer pushed this without a bounds check. Argus catches it, explains why, and generates a verified fix."

**Scenario 3: Subtle drift** (`demo_target/drift_withdrawal.py`)
```python
def withdraw(balance: int, amount: int) -> int:
    """Withdraw with fee — subtle overflow risk."""
    fee = amount // 10
    return balance - amount - fee
```
- Expected verdict: VULNERABLE
- Narrative: "This function looks safe at first glance, but the fee calculation can cause the result to go negative. Argus catches what code review might miss."

**Pre-generated backup artifacts:**
For each scenario, run the pipeline once with `--provider anthropic` and archive the output to `demo_target/backup_artifacts/`:
- `argus_report.json`
- `argus_dashboard.html`
- `Argus_Audit_Report.md`
- `.argus-trace/<run>/` (full trace)

These backup artifacts serve as fallback if the live demo encounters API issues or latency spikes.

**Acceptance**: All three demo scenarios run successfully with `python -m src.adapters.cli --file demo_target/<file>.py --allow-local-verify --provider anthropic`. Verdicts match expected outcomes. Backup artifacts are pre-generated and committed.

#### Step 4.6 — Demo script with precise timestamps
**New file**: `docs/demo-script.md`

A locked, rehearsable 3-minute script with exact timestamps, narration, and screen content for each beat.

**Script structure:**

```
## Segment 1: The Problem (0:00 – 0:25)
### Screen
- Split view: left = code editor with `vulnerable_transfer.py`, right = terminal
- Subtitle: "A developer pushes a transfer function without bounds checking"

### Narration
"Every day, developers push security-critical code changes. Code review catches
some issues, but subtle logic flaws — like missing bounds checks on financial
operations — slip through. A single unchecked subtraction can create money from
nothing. Current tools scan for patterns. Argus proves safety mathematically."

### Key visual
- Highlight the `return sender_balance - amount` line
- Show a negative input example: balance=100, amount=200 → result=-100

---

## Segment 2: Trigger (0:25 – 0:50)
### Screen
- GitLab MR view showing the vulnerable code pushed as a commit
- Argus CI job starts automatically
- Terminal shows: `python -m src.adapters.cli --mode ci --provider anthropic`

### Narration
"When a merge request is created, Argus triggers automatically. No manual
action required. The Argus agent discovers security obligations from the code,
translates them into Lean 4 proof obligations, and runs formal verification."

### Key visual
- Show the CI pipeline running with stage indicators
- Show "Argus Scanning..." status

---

## Segment 3: Detection + Diagnosis (0:50 – 1:25)
### Screen
- Terminal output showing obligation discovery
- Lean 4 proof code (from trace artifacts)
- Verification failure message

### Narration
"Argus found two obligations: the result must never be negative, and the
balance must not increase after withdrawal. The Lean 4 prover confirms:
without a bounds check, the first obligation fails. This isn't a heuristic —
it's a mathematical proof of the vulnerability."

### Key visual
- Show the Lean 4 proof with the failing obligation highlighted
- Show the Argus Dashboard "VULNERABLE" verdict card

---

## Segment 4: Repair + Re-verification (1:25 – 2:05)
### Screen
- Argus generates a repair using Claude
- Side-by-side: original vulnerable code vs. repaired code
- Re-verification succeeds

### Narration
"Argus uses Claude to generate a security patch. But it doesn't trust the
AI — it re-runs formal verification on the repaired code. The Lean 4 prover
confirms: both obligations now pass. The fix is mathematically proven safe.
Claude proposes, Lean disposes."

### Key visual
- Code diff: before (red) / after (green)
- Dashboard showing FIXED verdict with green checkmark
- "Claude proposes, Lean disposes" text overlay

---

## Segment 5: Developer & Compliance UX (2:05 – 2:35)
### Screen
- GitLab MR with Argus comment posted
- Mission Control dashboard in browser
- Downloadable audit artifacts

### Narration
"The developer sees a structured MR comment: what failed, why it matters,
and the verified fix. The Mission Control dashboard provides a visual overview
for security leads. SARIF reports integrate with GitLab's Security Dashboard.
Every decision is traceable — from obligation discovery through proof to verdict."

### Key visual
- MR comment with executive summary + repair diff
- Dashboard with pipeline timeline and verdict cards
- Artifact download panel

---

## Segment 6: Close (2:35 – 3:00)
### Screen
- Architecture diagram overlay
- Key metrics: "0 false positives across 18+ validation runs"
- Positioning statement

### Narration
"ArgusV2 is the trust layer for AI-accelerated software delivery. It
uses Anthropic Claude for reasoning and Lean 4 for mathematical proof.
It's autonomous, fail-closed, and enterprise-ready. Safer merges, faster
reviews, auditable trust."

### Key visual
- Architecture: LLM (advisor) → Formal Verifier (authority)
- "AI reasons. Math proves. Argus enforces."
```

**Backup plan:**
- If live run fails during recording: cut to pre-generated dashboard/artifacts
- If API is slow: use pre-recorded terminal output (screen recording of successful run)
- All backup assets reference the same code and version as the live demo

**Acceptance**: Script is exactly 3 minutes. Each segment has specific screen content, narration text, and key visuals. Script can be rehearsed with a stopwatch and consistently hits time marks.

#### Step 4.7 — Architecture diagram and visual assets
**New files**: `docs/architecture.md`, `docs/assets/` directory

Create text-based architecture diagrams suitable for:
- README (text/ASCII)
- Demo video overlay (rendered from text)
- Submission page (Devpost screenshot)

**Primary architecture diagram:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    GitLab Merge Request                         │
│                   (Event Trigger Layer)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ push / MR created
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Argus Verified Repair                        │
│                   (Autonomous Agent)                            │
│                                                                 │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Discover │→ │ Translate │→ │  Verify  │→ │   Enforce    │  │
│  │          │  │           │  │          │  │              │  │
│  │Obligations│ │Python→Lean│  │Lean 4 /  │  │ MR Comment   │  │
│  │& Inputs  │  │  / Dafny  │  │  Dafny   │  │ Labels       │  │
│  └──────────┘  └───────────┘  └────┬─────┘  │ Merge Gate   │  │
│                                    │         └──────────────┘  │
│                              ┌─────┴──────┐                    │
│                              │ Proof Fail? │                    │
│                              └─────┬──────┘                    │
│                         ┌──────────┼──────────┐                │
│                         ▼                     ▼                │
│                  ┌─────────────┐     ┌──────────────┐          │
│                  │Proof Search │     │Secure Repair │          │
│                  │(Claude)     │     │(Claude)      │          │
│                  └──────┬──────┘     └──────┬───────┘          │
│                         │                   │                  │
│                         └───────┬───────────┘                  │
│                                 ▼                              │
│                        ┌────────────────┐                      │
│                        │ Re-Verify      │                      │
│                        │ (Lean 4/Dafny) │                      │
│                        └────────────────┘                      │
│                                                                 │
│    ┌─────────────────────────────────────────────────────┐     │
│    │ TRUST MODEL: Claude = ADVISOR | Lean 4 = AUTHORITY  │     │
│    │ LLM proposes. Formal verifier decides. Always.      │     │
│    └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Output Artifacts                            │
│  ┌─────────┐ ┌──────────┐ ┌──────┐ ┌──────┐ ┌─────────────┐  │
│  │Dashboard│ │MR Comment│ │ JSON │ │SARIF │ │ Audit Trail │  │
│  │ (HTML)  │ │(GitLab)  │ │Report│ │Report│ │  (Traces)   │  │
│  └─────────┘ └──────────┘ └──────┘ └──────┘ └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Impact diagram (for demo close / submission):**
```
Without Argus                    With Argus
─────────────                    ──────────
Developer pushes code     →     Developer pushes code
Code review (manual)      →     Argus auto-verifies
Reviewer misses bug       →     Bug caught by proof
Bug reaches production    →     Fix generated + proven
Incident + rollback       →     Safe merge + audit trail
Hours/days of toil        →     Minutes, autonomous
```

**Acceptance**: Architecture diagram is committed to `docs/architecture.md`. Diagram accurately reflects the current pipeline stages and trust model. Can be copy-pasted into README and demo slides.

#### Step 4.8 — Tests for new dashboard and reporter functionality
**Files**: `tests/test_dashboard.py` (new), modify `tests/test_reporter.py`

**Dashboard tests (`test_dashboard.py`):**
- `test_generate_dashboard_produces_html` — Given a valid `argus_report.json`, generates HTML containing expected sections (header, summary, verdict cards)
- `test_dashboard_embeds_data` — Output HTML contains `<script type="application/json" id="argus-data">` with report data
- `test_dashboard_no_external_deps` — Output HTML contains no `<link>`, `<script src=`, or `fetch()` calls to external URLs
- `test_dashboard_handles_empty_report` — Empty file list produces a valid dashboard with "No files audited" message
- `test_dashboard_handles_all_verdicts` — Report with all 5 verdict types renders correctly

**Enhanced reporter tests:**
- `test_mr_comment_has_executive_summary` — Output contains "Executive Summary" and file count
- `test_mr_comment_groups_by_verdict` — VULNERABLE files appear under "Action Required", FIXED under "Auto-Repaired", VERIFIED under "Verified"
- `test_mr_comment_includes_repair_diff` — When `repaired_code` is provided for a FIXED file, output contains diff markers
- `test_mr_comment_backward_compatible` — Calling without `repaired_code`/`original_code` still produces valid comment (no crash)
- `test_markdown_report_has_risk_assessment` — Output contains "Risk Assessment" section

**Acceptance**: All new tests pass. Existing tests continue to pass (backward compatibility). Test coverage for reporter and dashboard modules is comprehensive.

#### Step 4.9 — README submission rewrite
**File**: `README.md`

Rewrite the README to be submission-grade. The README is the first thing judges see — it must communicate value, demonstrate the product, and guide them to evidence.

**Structure:**
1. **Hero line**: "ArgusV2 — The Trust Layer for AI-Accelerated Software Delivery"
2. **One-paragraph pitch**: What it does, why it matters, how it works (3 sentences max)
3. **Screenshot/GIF**: Mission Control dashboard screenshot (or pipeline output example)
4. **How it works**: 4-step explanation with architecture diagram
5. **Custom Public Agent & Flow**: (existing Phase 2 section — keep/update)
6. **Quick Start**: 3-step guide to see Argus in action
7. **Demo Video**: Link to video (placeholder until Phase 5)
8. **Anthropic Integration**: How Claude powers reasoning while Lean 4 proves safety
9. **Output Artifacts**: Table of all outputs (dashboard, MR comment, SARIF, JSON, traces)
10. **Project Structure**: Brief directory overview
11. **License**: CC0

**Acceptance**: A judge reading only the README can understand what Argus does, how it works, and how to try it — in under 2 minutes. README includes at least one visual (screenshot or architecture diagram).

### Deliverables summary
| # | Deliverable | File(s) | New/Modified |
|---|---|---|---|
| 4.1 | Mission Control HTML dashboard generator | `src/core/dashboard.py` | New |
| 4.2 | Enhanced MR comment template | `src/core/reporter.py` | Modified |
| 4.3 | Enhanced Markdown audit report | `src/core/reporter.py` | Modified |
| 4.4 | Pipeline integration (dashboard + enhanced reports) | `src/core/pipeline.py`, `src/adapters/cli.py`, `src/adapters/gitlab_adapter.py` | Modified |
| 4.5 | Demo scenario files + backup artifacts | `demo_target/*.py`, `demo_target/backup_artifacts/` | New |
| 4.6 | Demo script with timestamps | `docs/demo-script.md` | New |
| 4.7 | Architecture diagram + visual assets | `docs/architecture.md` | New |
| 4.8 | Tests for dashboard + enhanced reporter | `tests/test_dashboard.py`, `tests/test_reporter.py` | New + Modified |
| 4.9 | README submission rewrite | `README.md` | Modified |

### Acceptance criteria
- [ ] `argus_dashboard.html` is generated as a pipeline artifact, opens in any modern browser, and communicates Argus value to a non-technical viewer within 45 seconds
- [ ] Dashboard contains: executive summary, pipeline timeline, per-file verdict cards with expandable details, code panels (Lean proof + repaired code), audit trail metadata
- [ ] Dashboard is fully self-contained: no external CSS/JS/CDN dependencies, no network requests
- [ ] MR comment includes executive summary, verdict-grouped file sections, developer action items for VULNERABLE files, and repair diffs for FIXED files
- [ ] MR comment renders correctly in GitLab Flavored Markdown and stays under 65,535 character limit
- [ ] Markdown audit report includes executive summary, risk assessment, and recommendations
- [ ] All three demo scenarios (`demo_target/`) run successfully with expected verdicts
- [ ] Pre-generated backup artifacts exist for all demo scenarios
- [ ] Demo script is exactly 3 minutes with timestamped segments covering: problem → trigger → detection → repair → UX → close
- [ ] Architecture diagram accurately represents current pipeline stages and trust model
- [ ] README communicates product value within 2 minutes of reading
- [ ] All new and existing tests pass (`pytest tests/`)
- [ ] No regressions: existing JSON/SARIF/SAST report formats are unchanged
- [ ] CLI `--output-html` flag produces dashboard alongside all existing artifacts

### Evidence for review
- `argus_dashboard.html` sample (opened in browser, screenshot captured)
- MR comment rendering in GitLab (screenshot or preview)
- `Argus_Audit_Report.md` rendered preview
- Demo script with timestamps (`docs/demo-script.md`)
- Demo scenario run logs (all 3 scenarios × 1 run minimum)
- Architecture diagram (`docs/architecture.md`)
- Full test suite pass (`pytest tests/`)
- README.md (rendered in GitLab repo view)

### What does NOT change in Phase 4
These files/components are explicitly out of scope:
- `src/core/pipeline.py` core verification logic — only data surface changes (exposing `repaired_code`/`original_code` to reporters)
- `src/core/obligation_policy.py` — deterministic preconditions unchanged
- `src/core/translator/` — all translators unchanged
- `src/core/verifier/` — Lean 4 / Dafny backends unchanged
- `src/core/verdict.py` — verdict computation unchanged
- `src/core/llm_provider.py` — provider contract unchanged
- `src/core/ci_integrity.py` — CI gate suite unchanged
- `config.yml`, `.gitlab/duo/agent-config.yml`, `.gitlab/duo/flows/argus_verify.yml` — agent/flow definitions unchanged
- `benchmarks/seeded/` — automated test corpus unchanged (demo scenarios are separate in `demo_target/`)

### Security and compliance note
- Dashboard HTML must not include any API keys, tokens, or credentials in embedded data
- Dashboard must not make any network requests (fully offline/self-contained)
- Trace file paths shown in dashboard are relative, not absolute (no leaking of local filesystem paths)
- Demo backup artifacts must not contain any real API keys or sensitive data
- Pre-generated artifacts should be from runs against the benchmark/demo corpus only (no customer code)

### Risks specific to Phase 4
| Risk | Impact | Mitigation |
|---|---|---|
| Dashboard HTML is too complex / fragile | Maintenance burden, display bugs across browsers | Keep CSS/JS minimal; use semantic HTML (`<details>`, `<table>`, `<pre>`); test in Chrome, Firefox, Safari |
| MR comment exceeds GitLab character limit | Comment is truncated or fails to post | Track character count; truncate obligation details via collapsible sections; test with large file sets |
| Demo scenarios produce unexpected verdicts | Demo is unrehearsable or inconsistent | Use the simplest possible code patterns (same structure as benchmark corpus); pre-run and validate before locking |
| Demo timing is too tight / too loose | Script doesn't fit in 3 minutes | Time each segment during writing; allow ±5 seconds per segment; have a cut-able segment (Segment 5 can be shortened) |
| Legacy frontend expectations from judges | Judges expect a running web app | Dashboard HTML artifact + MR screenshot provides equivalent visual impact without server complexity; README makes it clear this is a CI-integrated agent, not a web app |
| README rewrite loses existing content | Phase 2 sections or quick start docs are accidentally removed | Preserve all Phase 2 sections verbatim; rewrite is additive (new sections + reorganization), not destructive |

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
