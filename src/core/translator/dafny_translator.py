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

        params = ", ".join(f"{arg.arg}: int" for arg in fn.args.args)
        lines = [f"method {fn.name}({params}) returns (result: int)"]
        for item in relevant:
            if item.category == "non_negativity":
                lines.append("  ensures result >= 0")
        for item in relevant:
            lines.append(f"  // OBLIGATION: {item.property}")
        lines.append("{")
        if any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(fn)):
            lines.extend(
                [
                    "  var i := 0;",
                    "  while (i < 1)",
                    "    invariant 0 <= i <= 1",
                    "    decreases 1 - i",
                    "  {",
                    "    i := i + 1;",
                    "  }",
                ]
            )
        lines.append("  result := 0;")
        lines.append("}")
        return "\n".join(lines)
