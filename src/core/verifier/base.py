from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from ..models import Obligation, ObligationResult


@dataclass
class VerificationOutcome:
    engine: str
    obligation_results: List[ObligationResult]
    raw_output: str
    verification_error: bool = False
    error_message: str = ""

    @property
    def all_passed(self) -> bool:
        return bool(self.obligation_results) and all(
            item.verified for item in self.obligation_results
        )


class Verifier(Protocol):
    def verify(self, proof_code: str, obligations: List[Obligation]) -> VerificationOutcome:
        ...

