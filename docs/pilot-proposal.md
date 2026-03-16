# ArgusV2 30-Day Pilot Proposal

## Scope
- 1 GitLab project, 5-20 active developers
- Advisory mode first, then optional enforced mode
- Target >=50 merge requests analyzed

## Success metrics
| Metric | Target |
|---|---|
| Confirmed true positive rate | >90% of VULNERABLE/FIXED findings validated by team |
| False VERIFIED rate | 0% |
| Developer satisfaction | >70% continue recommendation |
| Pipeline latency impact | <5 minutes for audited MR jobs |
| Coverage | >80% of eligible Python files |

## Timeline
- Week 0: setup and baseline validation
- Week 1-2: advisory operation + feedback loop
- Week 3: policy tuning and optional enforcement trial
- Week 4: review, ROI summary, go/no-go recommendation

## Inputs required from pilot team
- GitLab project admin access
- Provider key and MR publishing token
- Named engineering/security champion

## Deliverables
- Weekly verdict/latency summary
- End-of-pilot findings report
- Production rollout recommendation
