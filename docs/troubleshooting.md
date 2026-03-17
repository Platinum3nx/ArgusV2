# ArgusV2 Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ARGUS_PROXY_TOKEN is not set` | missing env var | set CI variable or export locally |
| `Provider 'gemini' is not supported in hosted mode` | unsupported provider in proxy mode | use `--provider anthropic` |
| `Unknown provider` | invalid `--provider` | use `anthropic` |
| `python: command not found` | environment path mismatch | use `python3` |
| Dashboard not generated | report missing or generation exception | verify `argus_report.json`, inspect warning output |
| No MR comment posted | token/scope/env missing | set `GITLAB_TOKEN` with `api`, ensure MR context vars |
| CI says no files to audit | all changed files excluded path | ensure audited files are under `src/` or eligible paths |
| Lean verifier unavailable | missing binary/runtime | use Docker image build or install Lean toolchain |
| Docker build fails | network/base image issue | retry build, verify image access |
| Unexpected UNVERIFIED | unsupported construct or guard failure | inspect `.argus-trace/.../02_semantic_guard.json` and refactor code |
| Different AI suggestions run-to-run | LLM nondeterminism | rely on verifier verdict, not suggestion text |
