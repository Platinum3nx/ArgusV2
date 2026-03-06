from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Union


class IRType(str, Enum):
    INT = "Int"
    BOOL = "Bool"
    LIST_INT = "List Int"


@dataclass(frozen=True)
class IRParam:
    name: str
    type: IRType


@dataclass(frozen=True)
class IRVar:
    name: str


@dataclass(frozen=True)
class IRIntLiteral:
    value: int


@dataclass(frozen=True)
class IRBoolLiteral:
    value: bool


@dataclass(frozen=True)
class IRListLiteral:
    items: List["IRExpr"]


@dataclass(frozen=True)
class IRUnaryOp:
    op: str
    operand: "IRExpr"


@dataclass(frozen=True)
class IRBinaryOp:
    op: str
    left: "IRExpr"
    right: "IRExpr"


@dataclass(frozen=True)
class IRCompare:
    op: str
    left: "IRExpr"
    right: "IRExpr"


@dataclass(frozen=True)
class IRBoolOp:
    op: str
    left: "IRExpr"
    right: "IRExpr"


@dataclass(frozen=True)
class IRIfThenElse:
    condition: "IRExpr"
    then_expr: "IRExpr"
    else_expr: "IRExpr"


@dataclass(frozen=True)
class IRLet:
    name: str
    value: "IRExpr"
    body: "IRExpr"


@dataclass(frozen=True)
class IRSubscript:
    collection: "IRExpr"
    index: "IRExpr"


@dataclass(frozen=True)
class IRLen:
    collection: "IRExpr"


@dataclass(frozen=True)
class IRConcat:
    left: "IRExpr"
    right: "IRExpr"


IRExpr = Union[
    IRVar,
    IRIntLiteral,
    IRBoolLiteral,
    IRListLiteral,
    IRUnaryOp,
    IRBinaryOp,
    IRCompare,
    IRBoolOp,
    IRIfThenElse,
    IRLet,
    IRSubscript,
    IRLen,
    IRConcat,
]


@dataclass(frozen=True)
class IRFunction:
    name: str
    params: List[IRParam]
    return_type: IRType
    body: IRExpr


@dataclass(frozen=True)
class IRProgram:
    functions: List[IRFunction]
