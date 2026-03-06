from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import List, Set

from .models import (
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
    IRParam,
    IRProgram,
    IRSubscript,
    IRType,
    IRUnaryOp,
    IRVar,
)


class LoweringError(RuntimeError):
    pass


@dataclass(frozen=True)
class LoweringOutcome:
    success: bool
    program: IRProgram | None
    unsupported_constructs: List[str]
    error: str = ""


class PythonIRLowerer:
    """
    Deterministic lowering from a strict Python subset into expression-oriented IR.
    """

    def lower(self, python_code: str) -> LoweringOutcome:
        try:
            tree = ast.parse(python_code)
        except SyntaxError as exc:
            return LoweringOutcome(
                success=False,
                program=None,
                unsupported_constructs=["syntax_error"],
                error=f"SyntaxError: {exc}",
            )

        unsupported = self._collect_unsupported(tree)
        if unsupported:
            return LoweringOutcome(
                success=False,
                program=None,
                unsupported_constructs=sorted(unsupported),
                error="Unsupported construct(s): " + ", ".join(sorted(unsupported)),
            )

        functions: List[IRFunction] = []
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            try:
                functions.append(self._lower_function(node))
            except LoweringError as exc:
                return LoweringOutcome(
                    success=False,
                    program=None,
                    unsupported_constructs=["lowering_error"],
                    error=f"{node.name}: {exc}",
                )

        if not functions:
            return LoweringOutcome(
                success=False,
                program=None,
                unsupported_constructs=["no_function_definitions"],
                error="No function definitions found",
            )

        return LoweringOutcome(
            success=True,
            program=IRProgram(functions=functions),
            unsupported_constructs=[],
        )

    def _collect_unsupported(self, tree: ast.AST) -> Set[str]:
        unsupported: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                unsupported.add("async_function")
            if isinstance(node, ast.ClassDef):
                unsupported.add("class_definition")
            if isinstance(node, ast.For):
                unsupported.add("for_loop")
            if isinstance(node, ast.While):
                unsupported.add("while_loop")
            if isinstance(node, ast.Await):
                unsupported.add("await_expression")
            if isinstance(node, ast.Yield):
                unsupported.add("generator_yield")
            if isinstance(node, (ast.Try, ast.With, ast.Lambda)):
                unsupported.add(type(node).__name__.lower())
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                unsupported.add("comprehension")
        return unsupported

    def _lower_function(self, fn: ast.FunctionDef) -> IRFunction:
        if fn.decorator_list:
            raise LoweringError("Decorators are not supported")
        if fn.args.vararg is not None or fn.args.kwarg is not None:
            raise LoweringError("Varargs and kwargs are not supported")
        if fn.args.kwonlyargs:
            raise LoweringError("Keyword-only arguments are not supported")

        params = [
            IRParam(name=arg.arg, type=self._annotation_to_type(arg.annotation))
            for arg in fn.args.args
        ]
        return_type = self._annotation_to_type(fn.returns)
        body = self._lower_stmt_sequence(self._strip_docstrings(fn.body))
        return IRFunction(name=fn.name, params=params, return_type=return_type, body=body)

    def _strip_docstrings(self, statements: List[ast.stmt]) -> List[ast.stmt]:
        out: List[ast.stmt] = []
        for stmt in statements:
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                continue
            out.append(stmt)
        return out

    def _lower_stmt_sequence(self, statements: List[ast.stmt]) -> IRExpr:
        if not statements:
            raise LoweringError("Function path does not return a value")

        first = statements[0]
        rest = statements[1:]

        if isinstance(first, ast.Return):
            if first.value is None:
                raise LoweringError("Return without value is not supported")
            return self._lower_expr(first.value)

        if isinstance(first, ast.Assign):
            if len(first.targets) != 1 or not isinstance(first.targets[0], ast.Name):
                raise LoweringError("Only single-name assignments are supported")
            if not rest:
                raise LoweringError("Assignment-only trailing statement is unsupported")
            target = first.targets[0].id
            value = self._lower_expr(first.value)
            return IRLet(name=target, value=value, body=self._lower_stmt_sequence(rest))

        if isinstance(first, ast.AnnAssign):
            if not isinstance(first.target, ast.Name) or first.value is None:
                raise LoweringError("Only named annotated assignments with values are supported")
            if not rest:
                raise LoweringError("Annotated assignment-only trailing statement is unsupported")
            value = self._lower_expr(first.value)
            return IRLet(
                name=first.target.id,
                value=value,
                body=self._lower_stmt_sequence(rest),
            )

        if isinstance(first, ast.If):
            then_statements = self._strip_docstrings(first.body) + rest
            else_statements = self._strip_docstrings(first.orelse) + rest
            if not then_statements or not else_statements:
                raise LoweringError("Conditional path does not return a value")
            return IRIfThenElse(
                condition=self._lower_expr(first.test),
                then_expr=self._lower_stmt_sequence(then_statements),
                else_expr=self._lower_stmt_sequence(else_statements),
            )

        if isinstance(first, ast.Pass):
            return self._lower_stmt_sequence(rest)

        raise LoweringError(f"Unsupported statement: {type(first).__name__}")

    def _lower_expr(self, expr: ast.AST) -> IRExpr:
        if isinstance(expr, ast.Name):
            return IRVar(name=expr.id)

        if isinstance(expr, ast.Constant):
            if isinstance(expr.value, bool):
                return IRBoolLiteral(value=expr.value)
            if isinstance(expr.value, int):
                return IRIntLiteral(value=expr.value)
            raise LoweringError(f"Unsupported constant: {expr.value!r}")

        if isinstance(expr, ast.UnaryOp):
            if isinstance(expr.op, ast.USub):
                return IRUnaryOp(op="-", operand=self._lower_expr(expr.operand))
            if isinstance(expr.op, ast.Not):
                return IRUnaryOp(op="not", operand=self._lower_expr(expr.operand))
            raise LoweringError(f"Unsupported unary op: {type(expr.op).__name__}")

        if isinstance(expr, ast.BinOp):
            left = self._lower_expr(expr.left)
            right = self._lower_expr(expr.right)
            if isinstance(expr.op, ast.Add):
                if isinstance(right, IRListLiteral):
                    return IRConcat(left=left, right=right)
                return IRBinaryOp(op="+", left=left, right=right)
            if isinstance(expr.op, ast.Sub):
                return IRBinaryOp(op="-", left=left, right=right)
            if isinstance(expr.op, ast.Mult):
                return IRBinaryOp(op="*", left=left, right=right)
            if isinstance(expr.op, (ast.Div, ast.FloorDiv)):
                return IRBinaryOp(op="/", left=left, right=right)
            if isinstance(expr.op, ast.Mod):
                return IRBinaryOp(op="%", left=left, right=right)
            raise LoweringError(f"Unsupported binary op: {type(expr.op).__name__}")

        if isinstance(expr, ast.BoolOp):
            op = "and" if isinstance(expr.op, ast.And) else "or"
            values = [self._lower_expr(item) for item in expr.values]
            if len(values) < 2:
                raise LoweringError("Boolean operation missing operands")
            current = values[0]
            for item in values[1:]:
                current = IRBoolOp(op=op, left=current, right=item)
            return current

        if isinstance(expr, ast.Compare):
            if len(expr.ops) != 1 or len(expr.comparators) != 1:
                raise LoweringError("Chained comparisons are not supported")
            op_map = {
                ast.Gt: ">",
                ast.GtE: ">=",
                ast.Lt: "<",
                ast.LtE: "<=",
                ast.Eq: "==",
                ast.NotEq: "!=",
                ast.In: "in",
                ast.NotIn: "not in",
            }
            symbol = op_map.get(type(expr.ops[0]))
            if symbol is None:
                raise LoweringError(f"Unsupported comparison op: {type(expr.ops[0]).__name__}")
            return IRCompare(
                op=symbol,
                left=self._lower_expr(expr.left),
                right=self._lower_expr(expr.comparators[0]),
            )

        if isinstance(expr, ast.IfExp):
            return IRIfThenElse(
                condition=self._lower_expr(expr.test),
                then_expr=self._lower_expr(expr.body),
                else_expr=self._lower_expr(expr.orelse),
            )

        if isinstance(expr, ast.List):
            return IRListLiteral(items=[self._lower_expr(item) for item in expr.elts])

        if isinstance(expr, ast.Subscript):
            return IRSubscript(
                collection=self._lower_expr(expr.value),
                index=self._lower_expr(expr.slice),
            )

        if isinstance(expr, ast.Call):
            if (
                isinstance(expr.func, ast.Name)
                and expr.func.id == "len"
                and len(expr.args) == 1
                and not expr.keywords
            ):
                return IRLen(collection=self._lower_expr(expr.args[0]))
            raise LoweringError("Only len(...) calls are supported")

        raise LoweringError(f"Unsupported expression: {type(expr).__name__}")

    def _annotation_to_type(self, annotation: ast.AST | None) -> IRType:
        if annotation is None:
            return IRType.INT
        if isinstance(annotation, ast.Name):
            if annotation.id == "int":
                return IRType.INT
            if annotation.id == "bool":
                return IRType.BOOL
            return IRType.INT
        if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
            container = annotation.value.id
            if container in {"list", "List"}:
                return IRType.LIST_INT
        return IRType.INT
