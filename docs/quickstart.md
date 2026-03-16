# ArgusV2 Quickstart (Hackathon Judge Path)

This guide gets you from fork to observable autonomous MR action in ~10 minutes.

## Prerequisites
- GitLab account with access to the GitLab AI Hackathon group
- A fork/clone of this repository
- Anthropic API key (primary reasoning engine)
- `GITLAB_TOKEN` (required for MR comment/label publishing)

## 1) Fork and configure

1. Fork this repository into the GitLab AI Hackathon group.
2. In **Settings → CI/CD → Variables**, add:
   - `ANTHROPIC_API_KEY` (required — primary reasoning engine)
   - `GITLAB_TOKEN` (required for MR comment/label publishing)
   - `GEMINI_API_KEY` (optional — for Gemini fallback via `--provider gemini`)
3. Ensure pipeline minutes/runners are available.

## 2) Trigger the autonomous flow

1. Create a branch and add or modify a Python file. Any `.py` file outside `tests/`,
   `benchmarks/`, and `legacy/` is audited — `demo_target/` is a good place.
2. Open a merge request into `main`.
3. The `argus-verify` job auto-runs on MR events (`$CI_MERGE_REQUEST_IID` rule).

## 3) Observe autonomous outputs

After pipeline completion, verify:
- MR comment posted with structured executive summary and verdict details (if `GITLAB_TOKEN` configured)
- Verdict labels applied (`argus:verified`, `argus:fixed`, `argus:vulnerable`)
- Artifacts generated:
  - `argus_dashboard.html` — Mission Control visual dashboard (open in browser)
  - `argus_report.json` — Machine-readable verdicts
  - `Argus_Audit_Report.md` — Executive summary + risk assessment
  - `argus-sarif-report.json` — SARIF 2.1.0 for security tooling
  - `gl-sast-report.json` — GitLab Security Dashboard integration
  - `argus-ci-gates.json` — 11-gate CI integrity results
  - `.argus-trace/` — Full audit trail with Lean proofs and repair artifacts

## 30-second local sanity run

```bash
# Set API key
export ANTHROPIC_API_KEY=<your-key>

# Audit a vulnerable file (safe scenario)
python -m src.adapters.cli \
  --file demo_target/safe_transfer.py \
  --allow-local-verify \
  --provider anthropic

# Open the dashboard
open argus_dashboard.html
```

## Demo scenarios

Three purpose-built scenarios show the full Argus story:

```bash
# Scenario 1: Already safe — Argus confirms via Lean 4
python -m src.adapters.cli --file demo_target/safe_transfer.py \
  --allow-local-verify --provider anthropic

# Scenario 2: Vulnerable → Argus catches + auto-repairs
python -m src.adapters.cli --file demo_target/vulnerable_transfer.py \
  --allow-local-verify --provider anthropic

# Scenario 3: Subtle drift — formal proof catches what review misses
python -m src.adapters.cli --file demo_target/drift_withdrawal.py \
  --allow-local-verify --provider anthropic
```

## Provider options

```bash
# Primary (default): Anthropic Claude
python -m src.adapters.cli --provider anthropic --file <file> --allow-local-verify

# Gemini fallback (requires GEMINI_API_KEY)
python -m src.adapters.cli --provider gemini --file <file> --allow-local-verify
```

## Judge verification map

| Evidence | Location |
|:---|:---|
| Agent identity | `config.yml`, `.gitlab/duo/agent-config.yml` |
| Public flow | `.gitlab/duo/flows/argus_verify.yml` |
| CI event trigger | `.gitlab-ci.yml` (`argus-verify` MR rules) |
| Anthropic integration | `src/core/llm_provider.py` — `AnthropicClient` |
| Test suite | `tests/` — 136 tests, 100% passing |
| Reliability evidence | `docs/reliability-report.md`, `artifacts/phase3/` |
| Demo script | `docs/demo-script.md` |
| Architecture | `docs/architecture.md` |
