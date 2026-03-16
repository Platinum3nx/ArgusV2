# ArgusV2 Enterprise Readiness

## Positioning
ArgusV2 targets platform engineering and application security teams that need merge-time security guarantees with auditable evidence.

## Ideal customer profile
- Teams using GitLab CI/CD
- Security/compliance-sensitive domains
- Need actionable MR-level security outcomes without manual bottlenecks

## Buyer personas
| Persona | Pain | Value delivered |
|---|---|---|
| VP Platform | review bottlenecks | autonomous pre-merge verification gates |
| AppSec Lead | alert fatigue | proof-gated outcomes and lower noise |
| Compliance Lead | evidence overhead | SARIF/JSON/Markdown + trace artifacts |

## Deployment maturity model
1. Advisory mode (labels/comments)
2. Enforced mode (non-zero CI on blocking verdicts)
3. Organization-specific policy extension

## UX validation checklist
- [x] Dashboard communicates run outcome quickly
- [x] MR comment is actionable and grouped by severity
- [x] Verdict definitions are explicit and consistent
- [x] Dashboard/report/MR summary remain consistent in stress test
- [ ] External non-engineer walkthrough signoff (manual)

## Evidence links
- `artifacts/phase5/mr-comment-stress.json`
- `artifacts/phase5/stress_dashboard.html`
- `docs/demo-script.md`
