from __future__ import annotations

import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import List

from ..models import Obligation, ObligationResult
from .base import VerificationOutcome


class DafnyVerifier:
    def __init__(self, timeout: int = 120, require_docker: bool = True) -> None:
        self.timeout = timeout
        self.require_docker = require_docker

    def verify(self, proof_code: str, obligations: List[Obligation]) -> VerificationOutcome:
        if self.require_docker and not self._running_in_docker() and not self._allow_local():
            return VerificationOutcome(
                engine="dafny",
                obligation_results=self._all_failed(obligations, "Docker-only verification is enabled"),
                raw_output="",
                verification_error=True,
                error_message="Docker-only verification is enabled (set ARGUS_ALLOW_LOCAL_VERIFY=true to override)",
            )

        path = Path(tempfile.gettempdir()) / f"argus_{uuid.uuid4().hex}.dfy"
        try:
            path.write_text(proof_code, encoding="utf-8")
            result = subprocess.run(
                ["dafny", "verify", str(path)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            output = (result.stdout + "\n" + result.stderr).strip()
            has_positive_error_count = re.search(r"\b([1-9][0-9]*)\s+errors?\b", output.lower()) is not None
            verified = result.returncode == 0 and not has_positive_error_count
            obligation_results = [
                ObligationResult(
                    obligation=item,
                    verified=verified,
                    engine="dafny",
                    message="" if verified else output[:400],
                )
                for item in obligations
            ]
            return VerificationOutcome(
                engine="dafny",
                obligation_results=obligation_results,
                raw_output=output,
                verification_error=False,
                error_message="" if verified else output[:400],
            )
        except Exception as exc:
            return VerificationOutcome(
                engine="dafny",
                obligation_results=self._all_failed(obligations, str(exc)),
                raw_output="",
                verification_error=True,
                error_message=str(exc),
            )
        finally:
            if path.exists():
                path.unlink()

    def _running_in_docker(self) -> bool:
        return Path("/.dockerenv").exists()

    def _allow_local(self) -> bool:
        return os.getenv("ARGUS_ALLOW_LOCAL_VERIFY", "false").lower() == "true"

    def _all_failed(self, obligations: List[Obligation], message: str) -> List[ObligationResult]:
        return [
            ObligationResult(obligation=item, verified=False, engine="dafny", message=message)
            for item in obligations
        ]
import re
