"""
Demo Scenario 2 — Vulnerable Transfer (expected verdict: FIXED or VULNERABLE)

This function is missing a bounds check. When `amount > sender_balance`,
the result goes negative — an attacker could create money from nothing.

Argus will:
  1. Detect the obligation failure via Lean 4 proof
  2. Use Claude to generate a verified repair
  3. Re-verify the repaired code formally
  4. Report FIXED (repaired) or VULNERABLE (if repair is insufficient)

Narrative: "A developer pushed this without a bounds check. Argus catches it,
explains why, generates a verified fix, and proves the fix is safe —
all before this reaches your main branch."
"""


def transfer(sender_balance: int, amount: int) -> int:
    """Transfer funds — missing bounds check!

    BUG: When amount > sender_balance, result is negative.
    Example: transfer(100, 200) == -100  <- funds created from nothing
    """
    return sender_balance - amount
