from src.core.ir import PythonIRLowerer, VerificationConditionGenerator
from src.core.models import Obligation


def _lower(code: str):
    outcome = PythonIRLowerer().lower(code)
    assert outcome.success
    assert outcome.program is not None
    return outcome.program


def test_vc_generator_nonneg_is_real_goal() -> None:
    program = _lower(
        """
def withdraw(balance: int, amount: int) -> int:
    return balance - amount
"""
    )
    obligations = [
        Obligation(
            id="withdraw:non_negative_result",
            property="withdraw(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    outcome = VerificationConditionGenerator().generate(program, obligations)
    assert outcome.success
    assert outcome.conditions[0].proposition != "True"
    assert "withdraw balance amount" in outcome.conditions[0].proposition


def test_vc_generator_uniqueness_extracts_membership_guard() -> None:
    program = _lower(
        """
def add_unique(items: list[int], value: int) -> list[int]:
    if value in items:
        return items
    return items + [value]
"""
    )
    obligations = [
        Obligation(
            id="add_unique:preserve_uniqueness",
            property="Collection updates preserve uniqueness where required",
            category="uniqueness",
            description="unique append",
        )
    ]
    outcome = VerificationConditionGenerator().generate(program, obligations)
    assert outcome.success
    assert "value ∉ items" in outcome.conditions[0].proposition
