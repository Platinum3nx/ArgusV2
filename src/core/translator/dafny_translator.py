from __future__ import annotations

import ast
from typing import List

from ..ir import PythonIRLowerer, VerificationConditionGenerator
from ..models import AssumedInput, Obligation
from .base import TranslationOutcome
from .dafny_ir_emitter import DafnyIREmitter


class DafnyTranslator:
    """Deterministic translator focused on loop-heavy code."""

    def __init__(self) -> None:
        self.lowerer = PythonIRLowerer()
        self.vc_generator = VerificationConditionGenerator()
        self.ir_emitter = DafnyIREmitter()

    def translate(
        self,
        python_code: str,
        obligations: List[Obligation],
        assumptions: List[AssumedInput],
    ) -> TranslationOutcome:
        lowered = self.lowerer.lower(python_code)
        if lowered.success and lowered.program is not None:
            vc_outcome = self.vc_generator.generate(lowered.program, obligations)
            if not vc_outcome.success:
                return TranslationOutcome(
                    success=False,
                    language="dafny",
                    code="",
                    translator="dafny",
                    error=vc_outcome.error or "VC generation failed",
                )
            code = self.ir_emitter.emit(lowered.program, vc_outcome.conditions)
            return TranslationOutcome(
                success=True,
                language="dafny",
                code=code,
                translator="dafny",
                used_llm=False,
            )

        unsupported = set(lowered.unsupported_constructs)
        if not unsupported.issubset({"for_loop", "while_loop"}):
            return TranslationOutcome(
                success=False,
                language="dafny",
                code="",
                translator="dafny",
                error=lowered.error or "Unsupported constructs for Dafny translation",
            )

        return self._translate_loop_fallback(python_code, obligations)

    def _translate_loop_fallback(
        self,
        python_code: str,
        obligations: List[Obligation],
    ) -> TranslationOutcome:
        try:
            tree = ast.parse(python_code)
        except SyntaxError as exc:
            return TranslationOutcome(
                success=False,
                language="dafny",
                code="",
                translator="dafny",
                error=f"SyntaxError: {exc}",
            )

        methods: List[str] = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                try:
                    methods.append(self._translate_function(node, obligations))
                except ValueError as exc:
                    return TranslationOutcome(
                        success=False,
                        language="dafny",
                        code="",
                        translator="dafny",
                        error=str(exc),
                    )

        if not methods:
            return TranslationOutcome(
                success=False,
                language="dafny",
                code="",
                translator="dafny",
                error="No function definitions found",
            )

        return TranslationOutcome(
            success=True,
            language="dafny",
            code="\n\n".join(methods),
            translator="dafny",
            used_llm=False,
        )

    def _translate_function(self, fn: ast.FunctionDef, obligations: List[Obligation]) -> str:
        relevant = [item for item in obligations if item.id.split(":", 1)[0] == fn.name]
        unsupported_categories = {
            item.category for item in relevant if item.category not in {"non_negativity", "loop_invariant"}
        }
        if unsupported_categories:
            raise ValueError(
                f"Unsupported obligation categories for DafnyTranslator: {sorted(unsupported_categories)}"
            )

        params = ", ".join(self._render_param(arg) for arg in fn.args.args)
        return_type = self._return_type(fn.returns)
        lines = [f"method {fn.name}({params}) returns (result: {return_type})"]
        for item in relevant:
            if item.category == "non_negativity" and return_type == "int":
                lines.append("  ensures result >= 0")
        for item in relevant:
            lines.append(f"  // OBLIGATION: {item.property}")
        lines.append("{")

        body = self._translate_statements(fn.body, indent="  ")
        lines.extend(body)

        if not any(isinstance(node, ast.Return) for node in ast.walk(fn)):
            raise ValueError(f"{fn.name}: function must return a value")

        lines.append("}")
        return "\n".join(lines)

    def _translate_statements(self, statements: List[ast.stmt], indent: str) -> List[str]:
        out: List[str] = []
        for stmt in statements:
            out.extend(self._translate_statement(stmt, indent=indent))
        return out

    def _translate_statement(self, stmt: ast.stmt, indent: str) -> List[str]:
        if isinstance(stmt, ast.Return):
            if stmt.value is None:
                raise ValueError("Return without value is unsupported")
            return [f"{indent}result := {self._render_expr(stmt.value)};"]

        if isinstance(stmt, ast.Assign):
            if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                raise ValueError("Only single-name assignments are supported")
            target = stmt.targets[0].id
            return [f"{indent}var {target} := {self._render_expr(stmt.value)};"]

        if isinstance(stmt, ast.AugAssign):
            if not isinstance(stmt.target, ast.Name):
                raise ValueError("Only name augmented assignments are supported")
            target = stmt.target.id
            op = self._render_binop(stmt.op)
            value = self._render_expr(stmt.value)
            return [f"{indent}{target} := {target} {op} {value};"]

        if isinstance(stmt, ast.If):
            test = self._render_expr(stmt.test)
            lines = [f"{indent}if ({test}) {{"]
            lines.extend(self._translate_statements(stmt.body, indent + "  "))
            lines.append(f"{indent}}}")
            if stmt.orelse:
                lines.append(f"{indent}else {{")
                lines.extend(self._translate_statements(stmt.orelse, indent + "  "))
                lines.append(f"{indent}}}")
            return lines

        if isinstance(stmt, ast.For):
            return self._translate_for(stmt, indent)

        if isinstance(stmt, ast.While):
            return self._translate_while(stmt, indent)

        if isinstance(stmt, ast.Pass):
            return [f"{indent}// pass"]

        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            return [f"{indent}// docstring"]

        raise ValueError(f"Unsupported statement in Dafny fallback: {type(stmt).__name__}")

    def _translate_for(self, stmt: ast.For, indent: str) -> List[str]:
        if not isinstance(stmt.target, ast.Name):
            raise ValueError("For-loop target must be a simple name")

        if not isinstance(stmt.iter, ast.Call) or not isinstance(stmt.iter.func, ast.Name) or stmt.iter.func.id != "range":
            raise ValueError("Only for-loops over range(...) are supported")

        if stmt.iter.keywords:
            raise ValueError("range(...) with keyword args is unsupported")

        if len(stmt.iter.args) == 1:
            start = "0"
            stop = self._render_expr(stmt.iter.args[0])
        elif len(stmt.iter.args) == 2:
            start = self._render_expr(stmt.iter.args[0])
            stop = self._render_expr(stmt.iter.args[1])
        else:
            raise ValueError("Only range(stop) and range(start, stop) are supported")

        idx = f"__argus_idx_{stmt.target.id}"
        lines = [
            f"{indent}var {idx} := {start};",
            f"{indent}while ({idx} < {stop})",
            f"{indent}  invariant {start} <= {idx} <= {stop}",
            f"{indent}  decreases {stop} - {idx}",
            f"{indent}{{",
            f"{indent}  var {stmt.target.id} := {idx};",
        ]
        lines.extend(self._translate_statements(stmt.body, indent + "  "))
        lines.append(f"{indent}  {idx} := {idx} + 1;")
        lines.append(f"{indent}}}")

        if stmt.orelse:
            lines.append(f"{indent}// Python for-else translated as post-loop block")
            lines.extend(self._translate_statements(stmt.orelse, indent))

        return lines

    def _translate_while(self, stmt: ast.While, indent: str) -> List[str]:
        cond = self._render_expr(stmt.test)
        decreases = self._infer_decreases(stmt.test)
        lines = [
            f"{indent}while ({cond})",
            f"{indent}  invariant true",
            f"{indent}  decreases {decreases}",
            f"{indent}{{",
        ]
        lines.extend(self._translate_statements(stmt.body, indent + "  "))
        lines.append(f"{indent}}}")
        if stmt.orelse:
            lines.append(f"{indent}// Python while-else translated as post-loop block")
            lines.extend(self._translate_statements(stmt.orelse, indent))
        return lines

    def _infer_decreases(self, test: ast.AST) -> str:
        if isinstance(test, ast.Compare) and len(test.ops) == 1 and len(test.comparators) == 1:
            left = self._render_expr(test.left)
            right = self._render_expr(test.comparators[0])
            op = test.ops[0]
            if isinstance(op, ast.Lt):
                return f"{right} - {left}"
            if isinstance(op, ast.Gt):
                return f"{left} - {right}"
            if isinstance(op, ast.LtE):
                return f"{right} - {left} + 1"
            if isinstance(op, ast.GtE):
                return f"{left} - {right} + 1"
        return "*"

    def _render_param(self, arg: ast.arg) -> str:
        return f"{arg.arg}: {self._annotation_to_dafny(arg.annotation)}"

    def _return_type(self, annotation: ast.AST | None) -> str:
        return self._annotation_to_dafny(annotation)

    def _annotation_to_dafny(self, annotation: ast.AST | None) -> str:
        if annotation is None:
            return "int"
        if isinstance(annotation, ast.Name):
            if annotation.id == "int":
                return "int"
            if annotation.id == "bool":
                return "bool"
            return "int"
        if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
            container = annotation.value.id
            if container in {"list", "List"}:
                return "seq<int>"
        return "int"

    def _render_expr(self, expr: ast.AST) -> str:
        if isinstance(expr, ast.Name):
            return expr.id
        if isinstance(expr, ast.Constant):
            if isinstance(expr.value, bool):
                return "true" if expr.value else "false"
            if isinstance(expr.value, int):
                return str(expr.value)
            raise ValueError(f"Unsupported constant: {expr.value!r}")
        if isinstance(expr, ast.UnaryOp):
            if isinstance(expr.op, ast.USub):
                return f"(-{self._render_expr(expr.operand)})"
            if isinstance(expr.op, ast.Not):
                return f"(!{self._render_expr(expr.operand)})"
            raise ValueError("Unsupported unary op")
        if isinstance(expr, ast.BinOp):
            return f"({self._render_expr(expr.left)} {self._render_binop(expr.op)} {self._render_expr(expr.right)})"
        if isinstance(expr, ast.BoolOp):
            op = "&&" if isinstance(expr.op, ast.And) else "||"
            values = [self._render_expr(item) for item in expr.values]
            if len(values) < 2:
                raise ValueError("Bool op needs at least two operands")
            current = values[0]
            for nxt in values[1:]:
                current = f"({current} {op} {nxt})"
            return current
        if isinstance(expr, ast.Compare):
            if len(expr.ops) != 1 or len(expr.comparators) != 1:
                raise ValueError("Chained comparisons are unsupported")
            left = self._render_expr(expr.left)
            right = self._render_expr(expr.comparators[0])
            op = self._render_cmp(expr.ops[0])
            return f"({left} {op} {right})"
        if isinstance(expr, ast.IfExp):
            return (
                f"(if {self._render_expr(expr.test)} then "
                f"{self._render_expr(expr.body)} else {self._render_expr(expr.orelse)})"
            )
        if isinstance(expr, ast.List):
            return "[" + ", ".join(self._render_expr(item) for item in expr.elts) + "]"
        if isinstance(expr, ast.Subscript):
            return f"{self._render_expr(expr.value)}[{self._render_expr(expr.slice)}]"
        if isinstance(expr, ast.Call):
            if (
                isinstance(expr.func, ast.Name)
                and expr.func.id == "len"
                and len(expr.args) == 1
                and not expr.keywords
            ):
                return f"|{self._render_expr(expr.args[0])}|"
            raise ValueError("Only len(...) calls are supported")
        raise ValueError(f"Unsupported expression in Dafny fallback: {type(expr).__name__}")

    def _render_binop(self, op: ast.operator) -> str:
        if isinstance(op, ast.Add):
            return "+"
        if isinstance(op, ast.Sub):
            return "-"
        if isinstance(op, ast.Mult):
            return "*"
        if isinstance(op, (ast.Div, ast.FloorDiv)):
            return "/"
        if isinstance(op, ast.Mod):
            return "%"
        raise ValueError(f"Unsupported binary operator: {type(op).__name__}")

    def _render_cmp(self, op: ast.cmpop) -> str:
        if isinstance(op, ast.Gt):
            return ">"
        if isinstance(op, ast.GtE):
            return ">="
        if isinstance(op, ast.Lt):
            return "<"
        if isinstance(op, ast.LtE):
            return "<="
        if isinstance(op, ast.Eq):
            return "=="
        if isinstance(op, ast.NotEq):
            return "!="
        if isinstance(op, ast.In):
            return "in"
        if isinstance(op, ast.NotIn):
            return "!in"
        raise ValueError(f"Unsupported comparison operator: {type(op).__name__}")
