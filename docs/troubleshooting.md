# ArgusV2 Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ANTHROPIC_API_KEY is not set` | missing env var | set CI variable or export locally |
| `GEMINI_API_KEY is not set` | missing env var | set CI variable or switch provider |
| `Unknown provider` | invalid `--provider` | use `anthropic` or `gemini` |
| `python: command not found` | environment path mismatch | use `python3` |
| Dashboard not generated | report missing or generation exception | verify `argus_report.json`, inspect warning output |
| No MR comment posted | token/scope/env missing | set `GITLAB_TOKEN` with `api`, ensure MR context vars |
| CI says no files to audit | all changed files excluded path | ensure audited files are under `src/` or eligible paths |
| Lean verifier unavailable | missing binary/runtime | use Docker image build or install Lean toolchain |
| Docker build fails | network/base image issue | retry build, verify image access |
| Unexpected UNVERIFIED | unsupported construct or guard failure | inspect `.argus-trace/.../02_semantic_guard.json` and refactor code |
| Different AI suggestions run-to-run | LLM nondeterminism | rely on verifier verdict, not suggestion text |
