from src.core.ir import PythonIRLowerer
from src.core.ir.models import IRBinaryOp, IRIfThenElse


def test_lowerer_preserves_guarded_return_structure() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    if amount > balance:
        return balance
    return balance - amount
"""
    outcome = PythonIRLowerer().lower(code)
    assert outcome.success
    assert outcome.program is not None

    fn = outcome.program.functions[0]
    assert isinstance(fn.body, IRIfThenElse)
    assert isinstance(fn.body.else_expr, IRBinaryOp)
    assert fn.body.else_expr.op == "-"


def test_lowerer_rejects_implicit_none_paths() -> None:
    code = """
def f(x: int) -> int:
    if x > 0:
        return x
"""
    outcome = PythonIRLowerer().lower(code)
    assert not outcome.success
    assert "does not return" in outcome.error


def test_lowerer_rejects_unsupported_type_annotation() -> None:
    code = """
def foo(x: float) -> int:
    return 1
"""
    outcome = PythonIRLowerer().lower(code)
    assert not outcome.success
    assert "Unsupported type annotation" in outcome.error
    assert "float" in outcome.error
