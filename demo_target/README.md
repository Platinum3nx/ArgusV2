# ArgusV2 Demo Scenarios

Three narrative-driven scenarios for demos, judging, and the submission video.
Each file is designed for maximum clarity to non-technical viewers.

## Scenario 1 — Safe (VERIFIED)
**File**: `safe_transfer.py`
**Expected verdict**: `VERIFIED`
**Narrative**: "This function is already safe. Argus confirms it mathematically."

```bash
python -m src.adapters.cli --file demo_target/safe_transfer.py \
  --allow-local-verify --provider anthropic
```

## Scenario 2 — Vulnerable → Auto-Repaired (FIXED)
**File**: `vulnerable_transfer.py`
**Expected verdict**: `FIXED` (repair succeeds) or `VULNERABLE` (repair insufficient)
**Narrative**: "Missing bounds check — Argus catches it, fixes it, and proves the fix."

```bash
python -m src.adapters.cli --file demo_target/vulnerable_transfer.py \
  --allow-local-verify --provider anthropic
```

## Scenario 3 — Subtle Drift (VULNERABLE)
**File**: `drift_withdrawal.py`
**Expected verdict**: `VULNERABLE`
**Narrative**: "Looks safe in review. Fails formal proof. Argus catches what humans miss."

```bash
python -m src.adapters.cli --file demo_target/drift_withdrawal.py \
  --allow-local-verify --provider anthropic
```

## Backup Artifacts
Pre-generated run artifacts are in `backup_artifacts/` — use these if the live
demo API is unavailable or too slow during recording.

## Full demo run (all three scenarios)
```bash
for f in safe_transfer vulnerable_transfer drift_withdrawal; do
  python -m src.adapters.cli \
    --file demo_target/${f}.py \
    --allow-local-verify \
    --provider anthropic \
    --output-json demo_target/backup_artifacts/${f}_report.json \
    --output-md demo_target/backup_artifacts/${f}_report.md \
    --output-html demo_target/backup_artifacts/${f}_dashboard.html
done
```
