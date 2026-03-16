# ArgusV2 Install & Validation Record

Date: 2026-03-16 (UTC)

## Environment
- Host: Linux x86_64
- Python: `python3`
- Repo path: `ArgusV2`

## Commands executed

### 1) Full test suite
```bash
PYTHONPATH=. python3 -m pytest tests -q
```
Result: **136 passed in 0.58s**

### 2) Provider-backed dry-run probe (Anthropic)
```bash
PYTHONPATH=. python3 -m src.adapters.cli --file demo_target/safe_transfer.py --allow-local-verify --provider anthropic --skip-gitlab-publish
```
Observed result:
```json
{"status":"configuration-error","error":"ANTHROPIC_API_KEY is not set..."}
```
Status: **expected fail-closed behavior confirmed**

### 3) Provider-backed dry-run probe (Gemini)
```bash
PYTHONPATH=. python3 -m src.adapters.cli --file demo_target/safe_transfer.py --allow-local-verify --provider gemini --skip-gitlab-publish
```
Observed result:
```json
{"status":"configuration-error","error":"GEMINI_API_KEY is not set..."}
```
Status: **expected fail-closed behavior confirmed**

### 4) Large-MR stress validation (Phase 4 carryover)
- Generated 30-file synthetic MR comment stress case:
  - artifact: `artifacts/phase5/mr-comment-stress.json`
  - result: `comment_chars=5751`, `within_limit=true`
- Generated stress dashboard:
  - artifact: `artifacts/phase5/stress_dashboard.html`

## Pass/fail matrix
- Test suite green: **PASS**
- Fail-closed provider config handling: **PASS**
- Large-MR comment limit validation: **PASS**
- Dashboard stress render generation: **PASS**
- End-to-end provider-backed demo scenario run: **PENDING (requires API key in environment)**

## Pending manual execution in keyed environment
Run once `ANTHROPIC_API_KEY` is available:
```bash
PYTHONPATH=. python3 -m src.adapters.cli --file demo_target/safe_transfer.py --allow-local-verify --provider anthropic
PYTHONPATH=. python3 -m src.adapters.cli --file demo_target/vulnerable_transfer.py --allow-local-verify --provider anthropic
PYTHONPATH=. python3 -m src.adapters.cli --file demo_target/drift_withdrawal.py --allow-local-verify --provider anthropic
```
Then archive outputs under `demo_target/backup_artifacts/` and update this file with verdicts + timestamps.
