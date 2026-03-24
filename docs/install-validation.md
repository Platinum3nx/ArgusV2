# ArgusV2 Install & Validation Record

Date: 2026-03-24 (UTC)

## Environment
- Host: macOS arm64
- Python: `python`
- Repo path: `ArgusV2`

## Commands executed

### 1) Full test suite
```bash
pytest
```
Result: **204 passed**

### 2) Hosted-provider live demo validation
```bash
python -m src.adapters.cli --file demo_target/safe_transfer.py --allow-local-verify --provider anthropic --skip-gitlab-publish
python -m src.adapters.cli --file demo_target/vulnerable_transfer.py --allow-local-verify --provider anthropic --skip-gitlab-publish
python -m src.adapters.cli --file demo_target/drift_withdrawal.py --allow-local-verify --provider anthropic --skip-gitlab-publish
```
Observed results:
- `safe_transfer.py` -> `VERIFIED` in `10.34s`
- `vulnerable_transfer.py` -> `FIXED` in `66.36s`
- `drift_withdrawal.py` -> `FIXED` in `57.43s`
- Archived outputs:
  - `demo_target/backup_artifacts/safe_transfer_*`
  - `demo_target/backup_artifacts/vulnerable_transfer_*`
  - `demo_target/backup_artifacts/drift_withdrawal_*`

### 3) Large-MR stress validation (Phase 4 carryover)
- Generated 30-file synthetic MR comment stress case:
  - artifact: `artifacts/phase5/mr-comment-stress.json`
  - result: `comment_chars=5751`, `within_limit=true`
- Generated stress dashboard:
  - artifact: `artifacts/phase5/stress_dashboard.html`

## Pass/fail matrix
- Test suite green: **PASS**
- Hosted-provider demo validation: **PASS**
- Large-MR comment limit validation: **PASS**
- Dashboard stress render generation: **PASS**
- End-to-end provider-backed demo scenario run: **PASS**
