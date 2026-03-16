"""
Demo Scenario 3 — Subtle Drift (expected verdict: VULNERABLE)

This function looks safe at first glance but has a subtle overflow risk.
The fee calculation can push the result below zero when both amount and fee
are deducted from a small balance.

This is the "drift" scenario: code that passes manual review but fails
formal proof. Demonstrates Argus's value over human-only code review.

Narrative: "This function looks safe. But the fee calculation means balance
can go negative: withdraw(10, 9) → 10 - 9 - 0 = 1 (ok), but
withdraw(10, 10) → 10 - 10 - 1 = -1 (negative balance!). Argus catches
what code review misses."
"""


def withdraw(balance: int, amount: int) -> int:
    """Withdraw funds with a 10% processing fee.

    BUG: fee is computed on amount, but both are subtracted from balance.
    When amount is at or near balance, the fee deduction pushes result negative.
    Example: withdraw(10, 10) == -1  <- unauthorized fund creation
    """
    fee = amount // 10
    return balance - amount - fee
