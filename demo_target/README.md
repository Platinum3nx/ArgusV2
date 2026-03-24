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
**Observed verdict in this checkout**: `FIXED`
**Narrative**: "Missing bounds check — Argus catches it, repairs it, and re-verifies the fix."

```bash
python -m src.adapters.cli --file demo_target/vulnerable_transfer.py \
  --allow-local-verify --provider anthropic
```

## Scenario 3 — Subtle Drift (FIXED)
**File**: `drift_withdrawal.py`
**Observed verdict in this checkout**: `FIXED`
**Narrative**: "Looks safe in review. Fails formal proof, then re-verifies after repair."

```bash
python -m src.adapters.cli --file demo_target/drift_withdrawal.py \
  --allow-local-verify --provider anthropic
```

## Backup Artifacts
The directory now contains fallback artifacts for all three scenarios plus
`PROVENANCE.md` with run metadata for the latest regeneration.

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
