# ArgusV2 Competitive Positioning

| Dimension | Traditional SAST | AI Code Review | ArgusV2 |
|---|---|---|---|
| Core method | pattern/rule matching | heuristic LLM feedback | formal proof + fail-closed verification |
| Trust model | trust scanner output | trust model suggestions | trust verifier; LLM is advisor only |
| Auto-fix confidence | low/unverified | low/varies | fix is re-verified before FIXED verdict |
| Auditability | scan reports | comment history | structured trace + SARIF + Markdown + JSON |
| Merge gating | possible but noisy | usually advisory | enforced by verdict + CI integrity gates |

## Differentiator statement
ArgusV2 does not ask teams to trust a probabilistic review comment. It requires proofs or returns blocking verdicts.

## Honest boundaries
- Coverage is strongest for supported Python/obligation patterns.
- Unsupported constructs intentionally fail closed and require manual review.
- Runtime depends on provider and verifier availability.
