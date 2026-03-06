"""Core intermediate representation and deterministic lowering utilities."""

from .chunker import IRChunk, IRChunker, IRLetBinding
from .lean_render import render_expr
from .lowerer import LoweringOutcome, PythonIRLowerer
from .models import IRFunction, IRParam, IRProgram, IRType
from .vc_generator import (
    VCGenerationOutcome,
    VerificationCondition,
    VerificationConditionGenerator,
)

__all__ = [
    "IRChunk",
    "IRChunker",
    "IRFunction",
    "IRLetBinding",
    "IRParam",
    "IRProgram",
    "IRType",
    "LoweringOutcome",
    "PythonIRLowerer",
    "VCGenerationOutcome",
    "VerificationCondition",
    "VerificationConditionGenerator",
    "render_expr",
]
