from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .models import IRExpr, IRFunction, IRIfThenElse, IRLet, IRUnaryOp


@dataclass(frozen=True)
class IRLetBinding:
    name: str
    value: IRExpr


@dataclass(frozen=True)
class IRChunk:
    id: str
    function_name: str
    path_conditions: List[IRExpr]
    bindings: List[IRLetBinding]
    result: IRExpr


class IRChunker:
    """
    Splits expression-oriented IR into path-sensitive chunks.
    """

    def chunk_function(self, fn: IRFunction) -> List[IRChunk]:
        chunks: List[IRChunk] = []
        self._walk(
            fn_name=fn.name,
            expr=fn.body,
            path_conditions=[],
            bindings=[],
            chunks=chunks,
        )
        return chunks

    def _walk(
        self,
        fn_name: str,
        expr: IRExpr,
        path_conditions: List[IRExpr],
        bindings: List[IRLetBinding],
        chunks: List[IRChunk],
    ) -> None:
        if isinstance(expr, IRLet):
            self._walk(
                fn_name=fn_name,
                expr=expr.body,
                path_conditions=path_conditions,
                bindings=bindings + [IRLetBinding(name=expr.name, value=expr.value)],
                chunks=chunks,
            )
            return

        if isinstance(expr, IRIfThenElse):
            self._walk(
                fn_name=fn_name,
                expr=expr.then_expr,
                path_conditions=path_conditions + [expr.condition],
                bindings=bindings,
                chunks=chunks,
            )
            self._walk(
                fn_name=fn_name,
                expr=expr.else_expr,
                path_conditions=path_conditions + [IRUnaryOp(op="not", operand=expr.condition)],
                bindings=bindings,
                chunks=chunks,
            )
            return

        chunk_id = f"{fn_name}:chunk_{len(chunks)}"
        chunks.append(
            IRChunk(
                id=chunk_id,
                function_name=fn_name,
                path_conditions=path_conditions,
                bindings=bindings,
                result=expr,
            )
        )
