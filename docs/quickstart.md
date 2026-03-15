# ArgusV2 Quickstart (Hackathon Judge Path)

This guide gets you from fork to observable autonomous MR action in ~10 minutes.

## Prerequisites
- GitLab account with access to the GitLab AI Hackathon group
- A fork/clone of this repository
- CI variable set in project settings:
  - `GEMINI_API_KEY` (optional but recommended for discovery/repair richness)
  - `GITLAB_TOKEN` (required for MR comment/label publishing)

## 1) Fork and configure
1. Fork this repository into the GitLab AI Hackathon group.
2. In **Settings → CI/CD → Variables**, add:
   - `GEMINI_API_KEY`
   - `GITLAB_TOKEN`
3. Ensure pipeline minutes/runners are available.

## 2) Trigger the autonomous flow
1. Create a branch and add or modify a Python file. Any `.py` file outside `tests/`, `benchmarks/`, and `legacy/` is audited — `demo_target/` is a good place to add a test file.
2. Open a merge request into `main`.
3. The `argus-verify` job auto-runs on MR events (`$CI_MERGE_REQUEST_IID` rule).

## 3) Observe autonomous outputs
After pipeline completion, verify:
- MR comment posted with structured verdict summary (if `GITLAB_TOKEN` configured)
- Verdict labels applied (`argus:verified`, `argus:fixed`, `argus:vulnerable`)
- Artifacts generated:
  - `argus_report.json`
  - `Argus_Audit_Report.md`
  - `argus-sarif-report.json`
  - `gl-sast-report.json`
  - `argus-ci-gates.json`
  - `.argus-trace/`

## 30-second local sanity run
```bash
python -m src.adapters.cli --file benchmarks/seeded/vulnerable/negative_withdrawal.py --allow-local-verify --skip-gitlab-publish
```

## Judge verification map
- Agent identity: `config.yml`, `.gitlab/duo/agent-config.yml`
- Public flow definition: `.gitlab/duo/flows/argus_verify.yml`
- Runtime trigger proof: `.gitlab-ci.yml` (`argus-verify` MR rules)
