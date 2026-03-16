# ArgusV2 Verification Report

| File | Verdict | Engine |
|:---|:---|:---|
| `benchmarks/seeded/vulnerable/negative_withdrawal.py` | VERIFIED | lean |

## benchmarks/seeded/vulnerable/negative_withdrawal.py
- Verdict: **VERIFIED**
- Engine: `lean`
- Message: All obligations passed
- Obligations:
  - `withdraw:non_negative_result`: withdraw(...) >= 0
- Assumptions:
  - `balance >= amount` (runtime_guard:service.logic.pre_withdraw_check)
  - `balance >= 0` (db_constraint:accounts_table.balance_check)
  - `amount > 0` (validator:WithdrawalRequest.amount)
  - `amount >= 0` (policy:obligation_policy:derive_preconditions)
