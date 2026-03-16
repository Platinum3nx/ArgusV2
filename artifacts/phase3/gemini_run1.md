# ArgusV2 Verification Report

| File | Verdict | Engine |
|:---|:---|:---|
| `safe/saturating_withdrawal.py` | UNVERIFIED | lean |
| `vulnerable/negative_withdrawal.py` | UNVERIFIED | lean |
| `drift/uniqueness_probe.py` | UNVERIFIED | lean |

## safe/saturating_withdrawal.py
- Verdict: **UNVERIFIED**
- Engine: `lean`
- Message: Assumption evidence validation failed
- Obligations:
  - `withdraw:non_negative_result`: withdraw(...) >= 0
- Assumptions:
  - `` (code_context:function_name)
  - `` (code_context:variable_name)
  - `balance >= 0` (policy:obligation_policy:derive_preconditions)
  - `amount >= 0` (policy:obligation_policy:derive_preconditions)

## vulnerable/negative_withdrawal.py
- Verdict: **UNVERIFIED**
- Engine: `lean`
- Message: Assumption evidence validation failed
- Obligations:
  - `withdraw:non_negative_result`: withdraw(...) >= 0
- Assumptions:
  - `is_integer(balance)` (code:def withdraw(balance: int, amount: int) -> int:)
  - `is_integer(amount)` (code:def withdraw(balance: int, amount: int) -> int:)
  - `balance >= 0` (policy:obligation_policy:derive_preconditions)
  - `amount >= 0` (policy:obligation_policy:derive_preconditions)

## drift/uniqueness_probe.py
- Verdict: **UNVERIFIED**
- Engine: `lean`
- Message: Assumption evidence validation failed
- Obligations:
  - `append_unique:preserve_uniqueness`: Collection updates preserve uniqueness where required
- Assumptions:
  - `` (python_type_hint:items: list[int])
  - `` (python_type_hint:value: int)
