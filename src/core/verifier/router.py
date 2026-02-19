from __future__ import annotations

import ast
from dataclasses import dataclass

from .dafny_verifier import DafnyVerifier
from .lean_verifier import LeanVerifier


@dataclass(frozen=True)
class EngineSelection:
    engine: str
    reason: str


class VerifierRouter:
    """
    Select verification engine once, before verification.
    No post-failure engine switching.
    """

    def __init__(self, lean: LeanVerifier, dafny: DafnyVerifier) -> None:
        self.lean = lean
        self.dafny = dafny

    def select_engine(self, python_code: str) -> EngineSelection:
        try:
            tree = ast.parse(python_code)
        except SyntaxError:
            return EngineSelection(engine="lean", reason="syntax_error_fallback")

        has_loops = any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree))
        if has_loops:
            return EngineSelection(engine="dafny", reason="loop_detected")
        return EngineSelection(engine="lean", reason="non_loop_code")

