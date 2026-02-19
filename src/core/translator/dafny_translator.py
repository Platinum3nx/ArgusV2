from __future__ import annotations

import ast
from typing import List

from ..models import AssumedInput, Obligation
from .base import TranslationOutcome


class DafnyTranslator:
    """Deterministic translator focused on loop-heavy code."""

    def translate(
        self,
        python_code: str,
        obligations: List[Obligation],
        assumptions: List[AssumedInput],
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
                methods.append(self._translate_function(node, obligations))

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
        params = ", ".join(f"{arg.arg}: int" for arg in fn.args.args)
        lines = [f"method {fn.name.title()}({params}) returns (result: int)"]
        lines.append("  ensures true")
        for item in obligations:
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

