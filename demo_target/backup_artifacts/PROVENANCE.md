# Backup Artifact Provenance

This directory stores fallback demo artifacts generated from real Argus runs.

For each scenario include:
- commit hash
- exact command
- UTC timestamp
- observed verdict
- generated artifact list

## Current status
Provider-backed regeneration completed on 2026-03-24 UTC using the hosted proxy path.

- Commit: `aa5f415`
- Model: `claude-sonnet-4-6`
- Token-backed command form:
  - `python -m src.adapters.cli --file demo_target/<scenario>.py --allow-local-verify --provider anthropic --skip-gitlab-publish ...`

### Latest archived runs

1. `safe_transfer.py`
   - Timestamp: `2026-03-24T04:05:11.210214+00:00`
   - Verdict: `VERIFIED`
   - Artifacts:
     - `safe_transfer_report.json`
     - `safe_transfer_report.md`
     - `safe_transfer_report.sarif.json`
     - `safe_transfer_gl_sast.json`
     - `safe_transfer_dashboard.html`

2. `vulnerable_transfer.py`
   - Timestamp: `2026-03-24T04:12:02.611730+00:00`
   - Verdict: `FIXED`
   - Artifacts:
     - `vulnerable_transfer_report.json`
     - `vulnerable_transfer_report.md`
     - `vulnerable_transfer_report.sarif.json`
     - `vulnerable_transfer_gl_sast.json`
     - `vulnerable_transfer_dashboard.html`

3. `drift_withdrawal.py`
   - Timestamp: `2026-03-24T04:13:05.007392+00:00`
   - Verdict: `FIXED`
   - Artifacts:
     - `drift_withdrawal_report.json`
     - `drift_withdrawal_report.md`
     - `drift_withdrawal_report.sarif.json`
     - `drift_withdrawal_gl_sast.json`
     - `drift_withdrawal_dashboard.html`
