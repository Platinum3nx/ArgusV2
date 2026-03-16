# ArgusV2 Operations Runbook

## Monitoring signals
| Signal | Source | Threshold | Response |
|---|---|---|---|
| CI failure rate | GitLab pipelines | >5% ERROR over 24h | inspect provider/verifier failures |
| Verdict drift | `argus_report.json` trend | sudden spike in VULNERABLE | validate recent code/policy changes |
| Provider availability | job logs | repeated timeout/config errors | rotate key, switch provider, retry |
| Artifact completeness | CI artifacts list | missing required outputs | inspect CLI run and permissions |

## Incident playbooks
### Provider outage / key failure
1. Confirm `ConfigurationError` details from logs.
2. Verify CI variable exists and is masked.
3. Switch provider (`LLM_PROVIDER=gemini`) if Anthropic outage; re-run.
4. Keep merge gate blocking until successful rerun.

### Verifier/runtime failure
1. Check `03_verify_stdout.txt` in trace.
2. Confirm Lean/Dafny binaries are available in image.
3. Retry pipeline once; if reproducible, open blocker issue and keep non-merge verdict.

### MR publish failure
1. Validate `GITLAB_TOKEN` scope (`api`).
2. Confirm `CI_PROJECT_ID` and `CI_MERGE_REQUEST_IID` present.
3. Treat publish as visibility failure, not proof correctness failure; artifacts remain source of truth.

## Routine maintenance
- Rotate provider and GitLab tokens monthly/quarterly.
- Re-run seeded benchmark + CI integrity after core changes.
- Review artifact retention (`expire_in`) and storage usage monthly.

## Pilot support expectations
- Business-hours best effort support
- Scope: configuration, deployment, verdict interpretation
- Out of scope: custom legal/compliance attestations beyond published docs
