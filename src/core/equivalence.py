from __future__ import annotations

import ast
import random
from dataclasses import dataclass
from typing import Any, Dict, List

from .ir import PythonIRLowerer
from .ir.models import (
    IRBinaryOp,
    IRBoolLiteral,
    IRBoolOp,
    IRCompare,
    IRConcat,
    IRExpr,
    IRFunction,
    IRIfThenElse,
    IRIntLiteral,
    IRLen,
    IRLet,
    IRListLiteral,
    IRSubscript,
    IRType,
    IRUnaryOp,
    IRVar,
)


@dataclass(frozen=True)
class EquivalenceIssue:
    function: str
    inputs: Dict[str, Any]
    python_result: str
    ir_result: str
    reason: str


@dataclass(frozen=True)
class EquivalenceResult:
    passed: bool
    cases_checked: int
    issues: List[EquivalenceIssue]


def run_equivalence_check(
    python_code: str,
    trials_per_function: int = 24,
    seed: int = 17,
) -> EquivalenceResult:
    lowered = PythonIRLowerer().lower(python_code)
    if not lowered.success or lowered.program is None:
        reason = lowered.error or "Lowering failed"
        return EquivalenceResult(
            passed=False,
            cases_checked=0,
            issues=[
                EquivalenceIssue(
                    function="<module>",
                    inputs={},
                    python_result="<n/a>",
                    ir_result="<n/a>",
                    reason=reason,
                )
            ],
        )

    try:
        tree = ast.parse(python_code)
    except SyntaxError as exc:
        return EquivalenceResult(
            passed=False,
            cases_checked=0,
            issues=[
                EquivalenceIssue(
                    function="<module>",
                    inputs={},
                    python_result="<n/a>",
                    ir_result="<n/a>",
                    reason=f"SyntaxError: {exc}",
                )
            ],
        )

    ast_functions = {
        item.name: item for item in tree.body if isinstance(item, ast.FunctionDef)
    }
    issues: List[EquivalenceIssue] = []
    checked = 0

    for fn in lowered.program.functions:
        ast_fn = ast_functions.get(fn.name)
        if ast_fn is None:
            issues.append(
                EquivalenceIssue(
                    function=fn.name,
                    inputs={},
                    python_result="<missing>",
                    ir_result="<n/a>",
                    reason="Function missing from parsed AST",
                )
            )
            continue

        rng = random.Random(f"{seed}:{fn.name}")
        for _ in range(trials_per_function):
            inputs = _sample_inputs(fn, rng)
            py_ok, py_result = _safe_eval_python_fn(ast_fn, dict(inputs))
            ir_ok, ir_result = _safe_eval_ir_fn(fn, dict(inputs))
            checked += 1

            if py_ok != ir_ok or py_result != ir_result:
                issues.append(
                    EquivalenceIssue(
                        function=fn.name,
                        inputs=inputs,
                        python_result=repr(py_result),
                        ir_result=repr(ir_result),
                        reason="AST/IR semantic mismatch",
                    )
                )
                break

    return EquivalenceResult(passed=not issues, cases_checked=checked, issues=issues)


def _sample_inputs(fn: IRFunction, rng: random.Random) -> Dict[str, Any]:
    sample: Dict[str, Any] = {}
    for param in fn.params:
        if param.type == IRType.INT:
            sample[param.name] = rng.randint(-6, 6)
        elif param.type == IRType.BOOL:
            sample[param.name] = bool(rng.randint(0, 1))
        elif param.type == IRType.LIST_INT:
            length = rng.randint(0, 4)
            sample[param.name] = [rng.randint(-3, 3) for _ in range(length)]
        else:
            sample[param.name] = rng.randint(-6, 6)
    return sample


def _safe_eval_python_fn(fn: ast.FunctionDef, env: Dict[str, Any]) -> tuple[bool, Any]:
    try:
        return True, _eval_python_statements(fn.body, env)
    except Exception as exc:
        return False, f"{type(exc).__name__}:{exc}"


def _safe_eval_ir_fn(fn: IRFunction, env: Dict[str, Any]) -> tuple[bool, Any]:
    try:
        return True, _eval_ir_expr(fn.body, env)
    except Exception as exc:
        return False, f"{type(exc).__name__}:{exc}"


def _eval_python_statements(statements: List[ast.stmt], env: Dict[str, Any]) -> Any:
    cleaned = [
        stmt
        for stmt in statements
        if not (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        )
    ]
    if not cleaned:
        raise RuntimeError("Function path does not return")

    first = cleaned[0]
    rest = cleaned[1:]

    if isinstance(first, ast.Return):
        if first.value is None:
            raise RuntimeError("Return without value")
        return _eval_python_expr(first.value, env)

    if isinstance(first, ast.Assign):
        if len(first.targets) != 1 or not isinstance(first.targets[0], ast.Name):
            raise RuntimeError("Unsupported assignment form")
        env[first.targets[0].id] = _eval_python_expr(first.value, env)
        return _eval_python_statements(rest, env)

    if isinstance(first, ast.AnnAssign):
        if not isinstance(first.target, ast.Name) or first.value is None:
            raise RuntimeError("Unsupported annotated assignment")
        env[first.target.id] = _eval_python_expr(first.value, env)
        return _eval_python_statements(rest, env)

    if isinstance(first, ast.If):
        cond = bool(_eval_python_expr(first.test, env))
        branch = first.body if cond else first.orelse
        return _eval_python_statements(branch + rest, env)

    if isinstance(first, ast.Pass):
        return _eval_python_statements(rest, env)

    raise RuntimeError(f"Unsupported statement: {type(first).__name__}")


def _eval_python_expr(expr: ast.AST, env: Dict[str, Any]) -> Any:
    if isinstance(expr, ast.Name):
        return env[expr.id]
    if isinstance(expr, ast.Constant):
        if isinstance(expr.value, (int, bool)):
            return expr.value
        raise RuntimeError(f"Unsupported constant: {expr.value!r}")
    if isinstance(expr, ast.UnaryOp):
        value = _eval_python_expr(expr.operand, env)
        if isinstance(expr.op, ast.USub):
            return -value
        if isinstance(expr.op, ast.Not):
            return not value
        raise RuntimeError("Unsupported unary op")
    if isinstance(expr, ast.BinOp):
        left = _eval_python_expr(expr.left, env)
        right = _eval_python_expr(expr.right, env)
        if isinstance(expr.op, ast.Add):
            return left + right
        if isinstance(expr.op, ast.Sub):
            return left - right
        if isinstance(expr.op, ast.Mult):
            return left * right
        if isinstance(expr.op, (ast.Div, ast.FloorDiv)):
            return left // right
        if isinstance(expr.op, ast.Mod):
            return left % right
        raise RuntimeError("Unsupported binary op")
    if isinstance(expr, ast.BoolOp):
        values = [_eval_python_expr(item, env) for item in expr.values]
        if isinstance(expr.op, ast.And):
            return all(values)
        if isinstance(expr.op, ast.Or):
            return any(values)
        raise RuntimeError("Unsupported bool op")
    if isinstance(expr, ast.Compare):
        if len(expr.ops) != 1 or len(expr.comparators) != 1:
            raise RuntimeError("Unsupported chained comparison")
        left = _eval_python_expr(expr.left, env)
        right = _eval_python_expr(expr.comparators[0], env)
        op = expr.ops[0]
        if isinstance(op, ast.Gt):
            return left > right
        if isinstance(op, ast.GtE):
            return left >= right
        if isinstance(op, ast.Lt):
            return left < right
        if isinstance(op, ast.LtE):
            return left <= right
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        if isinstance(op, ast.In):
            return left in right
        if isinstance(op, ast.NotIn):
            return left not in right
        raise RuntimeError("Unsupported comparison op")
    if isinstance(expr, ast.IfExp):
        cond = _eval_python_expr(expr.test, env)
        return _eval_python_expr(expr.body if cond else expr.orelse, env)
    if isinstance(expr, ast.List):
        return [_eval_python_expr(item, env) for item in expr.elts]
    if isinstance(expr, ast.Subscript):
        collection = _eval_python_expr(expr.value, env)
        index = _eval_python_expr(expr.slice, env)
        return collection[index]
    if isinstance(expr, ast.Call):
        if (
            isinstance(expr.func, ast.Name)
            and expr.func.id == "len"
            and len(expr.args) == 1
            and not expr.keywords
        ):
            return len(_eval_python_expr(expr.args[0], env))
        raise RuntimeError("Unsupported call expression")
    raise RuntimeError(f"Unsupported expression: {type(expr).__name__}")


def _eval_ir_expr(expr: IRExpr, env: Dict[str, Any]) -> Any:
    if isinstance(expr, IRVar):
        return env[expr.name]
    if isinstance(expr, IRIntLiteral):
        return expr.value
    if isinstance(expr, IRBoolLiteral):
        return expr.value
    if isinstance(expr, IRListLiteral):
        return [_eval_ir_expr(item, env) for item in expr.items]
    if isinstance(expr, IRUnaryOp):
        value = _eval_ir_expr(expr.operand, env)
        if expr.op == "-":
            return -value
        if expr.op == "not":
            return not value
    if isinstance(expr, IRBinaryOp):
        left = _eval_ir_expr(expr.left, env)
        right = _eval_ir_expr(expr.right, env)
        if expr.op == "+":
            return left + right
        if expr.op == "-":
            return left - right
        if expr.op == "*":
            return left * right
        if expr.op == "/":
            return left // right
        if expr.op == "%":
            return left % right
    if isinstance(expr, IRCompare):
        left = _eval_ir_expr(expr.left, env)
        right = _eval_ir_expr(expr.right, env)
        if expr.op == ">":
            return left > right
        if expr.op == ">=":
            return left >= right
        if expr.op == "<":
            return left < right
        if expr.op == "<=":
            return left <= right
        if expr.op == "==":
            return left == right
        if expr.op == "!=":
            return left != right
        if expr.op == "in":
            return left in right
        if expr.op == "not in":
            return left not in right
    if isinstance(expr, IRBoolOp):
        left = bool(_eval_ir_expr(expr.left, env))
        right = bool(_eval_ir_expr(expr.right, env))
        if expr.op == "and":
            return left and right
        if expr.op == "or":
            return left or right
    if isinstance(expr, IRIfThenElse):
        cond = bool(_eval_ir_expr(expr.condition, env))
        return _eval_ir_expr(expr.then_expr if cond else expr.else_expr, env)
    if isinstance(expr, IRLet):
        value = _eval_ir_expr(expr.value, env)
        next_env = dict(env)
        next_env[expr.name] = value
        return _eval_ir_expr(expr.body, next_env)
    if isinstance(expr, IRSubscript):
        collection = _eval_ir_expr(expr.collection, env)
        index = int(_eval_ir_expr(expr.index, env))
        nat_index = max(index, 0)
        return collection[nat_index]
    if isinstance(expr, IRLen):
        collection = _eval_ir_expr(expr.collection, env)
        return len(collection)
    if isinstance(expr, IRConcat):
        return _eval_ir_expr(expr.left, env) + _eval_ir_expr(expr.right, env)

    raise RuntimeError(f"Unsupported IR expression: {type(expr).__name__}")
