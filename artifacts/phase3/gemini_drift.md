# ArgusV2 Verification Report

| File | Verdict | Engine |
|:---|:---|:---|
| `benchmarks/seeded/drift/uniqueness_probe.py` | VULNERABLE | lean |

## benchmarks/seeded/drift/uniqueness_probe.py
- Verdict: **VULNERABLE**
- Engine: `lean`
- Message: One or more canonical obligations failed
- Obligations:
  - `append_unique:preserve_uniqueness`: Collection updates preserve uniqueness where required
- Assumptions:
