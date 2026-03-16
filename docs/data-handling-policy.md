# ArgusV2 Data Handling Policy

## Data flow
1. Audited source code enters pipeline from repository files.
2. Selected stages send prompt payloads to configured LLM provider.
3. Verification outputs and verdicts are written to local trace and CI artifacts.
4. Optional MR publishing sends summary text/labels to GitLab API.

## Data classes
| Data | Where processed | Retention |
|---|---|---|
| Source code under audit | Runner filesystem + trace artifacts | CI job/artifact retention policy |
| LLM prompt/response content | Provider API + trace artifacts | Provider policy + artifact retention |
| Verdicts/obligations | JSON/SARIF/Markdown/HTML artifacts | Artifact retention |
| API keys/tokens | CI/CD variables only | Until rotated |

## Prompt policy
Prompts may include:
- function source snippets
- obligation text
- verifier error output

Prompts must not include:
- API keys/tokens/secrets
- unrelated environment values

## Retention/deletion guidance
- Configure artifact `expire_in` to match org policy.
- Treat `.argus-trace/` as auditable security evidence; avoid long-lived local storage on shared hosts.

## Compliance note
If repository code contains personal data, the configured LLM provider terms apply to that payload. Teams are responsible for provider compliance review before production rollout.
