from __future__ import annotations

from typing import List

from ..ir import PythonIRLowerer, VerificationConditionGenerator
from ..models import AssumedInput, Obligation
from .base import TranslationOutcome
from .lean_ir_emitter import LeanIREmitter


class ASTTranslator:
    """Deterministic translator backed by a shared Core IR."""

    def __init__(self) -> None:
        self.lowerer = PythonIRLowerer()
        self.vc_generator = VerificationConditionGenerator()
        self.emitter = LeanIREmitter()

    def translate(
        self,
        python_code: str,
        obligations: List[Obligation],
        assumptions: List[AssumedInput],
    ) -> TranslationOutcome:
        lowered = self.lowerer.lower(python_code)
        if not lowered.success or lowered.program is None:
            unsupported = set(lowered.unsupported_constructs)
            if {"for_loop", "while_loop", "async_function"} & unsupported:
                message = "Unsupported construct for ASTTranslator (loop/async)"
            else:
                message = lowered.error or "Lowering failed"
            return TranslationOutcome(
                success=False,
                language="lean",
                code="",
                translator="ast",
                error=message,
            )

        vc_outcome = self.vc_generator.generate(lowered.program, obligations)
        if not vc_outcome.success:
            return TranslationOutcome(
                success=False,
                language="lean",
                code="",
                translator="ast",
                error=vc_outcome.error or "VC generation failed",
            )

        code = self.emitter.emit(
            program=lowered.program,
            conditions=vc_outcome.conditions,
            assumptions=assumptions,
        )
        return TranslationOutcome(
            success=True,
            language="lean",
            code=code,
            translator="ast",
            used_llm=False,
        )
