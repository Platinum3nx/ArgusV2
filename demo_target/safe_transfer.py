"""
Demo Scenario 1 — Safe Transfer (expected verdict: VERIFIED)

This function correctly enforces bounds on both the amount and the balance.
Argus will confirm it satisfies all security obligations via Lean 4 formal proof.

Narrative: "This function is already safe. Argus confirms it mathematically —
no human judgment required."
"""


def transfer(sender_balance: int, amount: int) -> int:
    """Transfer funds with proper bounds checking.

    Obligations verified by Argus:
      - Result is non-negative (no negative balance creation)
      - Result does not exceed the original balance (no fund creation)
      - Zero amount is handled gracefully (idempotent)
    """
    if amount <= 0:
        return sender_balance
    if amount > sender_balance:
        return sender_balance
    return sender_balance - amount
