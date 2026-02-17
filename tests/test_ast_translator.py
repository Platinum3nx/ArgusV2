from src.core.models import Obligation
from src.core.translator.ast_translator import ASTTranslator


def test_ast_translator_translates_simple_function() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    return balance - amount
"""
    obligations = [
        Obligation(
            id="withdraw:non_negative_result",
            property="withdraw(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    outcome = ASTTranslator().translate(code, obligations, [])
    assert outcome.success
    assert "def withdraw" in outcome.code
    assert "theorem withdraw_non_negative_result" in outcome.code


def test_ast_translator_rejects_loops() -> None:
    code = """
def total(xs: list[int]) -> int:
    s = 0
    for x in xs:
        s += x
    return s
"""
    outcome = ASTTranslator().translate(code, [], [])
    assert not outcome.success
    assert "Unsupported construct" in outcome.error

