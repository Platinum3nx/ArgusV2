# ArgusV2 Verification Report

| File | Verdict | Engine |
|:---|:---|:---|
| `benchmarks/seeded/safe/saturating_withdrawal.py` | VERIFIED | lean |

## benchmarks/seeded/safe/saturating_withdrawal.py
- Verdict: **VERIFIED**
- Engine: `lean`
- Message: All obligations passed
- Obligations:
  - `withdraw:non_negative_result`: withdraw(...) >= 0
- Assumptions:
  - `balance >= 0` (db_constraint:accounts.balance.CHECK)
  - `amount >= 0` (validator:WithdrawalRequest.amount)
