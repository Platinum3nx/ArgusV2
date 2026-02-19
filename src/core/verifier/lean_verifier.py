from __future__ import annotations

import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import List

from ..models import Obligation, ObligationResult
from .base import VerificationOutcome


class LeanVerifier:
    def __init__(
        self,
        project_dir: str | None = None,
        timeout: int = 60,
        require_docker: bool = True,
    ) -> None:
        self.project_dir = project_dir
        self.timeout = timeout
        self.require_docker = require_docker

    def verify(self, proof_code: str, obligations: List[Obligation]) -> VerificationOutcome:
        if self.require_docker and not self._running_in_docker() and not self._allow_local():
            return VerificationOutcome(
                engine="lean",
                obligation_results=self._all_failed(obligations, "Docker-only verification is enabled"),
                raw_output="",
                verification_error=True,
                error_message="Docker-only verification is enabled (set ARGUS_ALLOW_LOCAL_VERIFY=true to override)",
            )

        project_dir = self._resolve_project_dir()
        filename = f"argus_{uuid.uuid4().hex}.lean"
        file_path = project_dir / filename

        try:
            file_path.write_text(proof_code, encoding="utf-8")
            command = ["lake", "env", "lean", filename]
            result = subprocess.run(
                command,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            output = (result.stdout + "\n" + result.stderr).strip()

            verified = result.returncode == 0 and "sorry" not in proof_code
            obligation_results = [
                ObligationResult(
                    obligation=item,
                    verified=verified,
                    engine="lean",
                    message="" if verified else output[:400],
                )
                for item in obligations
            ]
            return VerificationOutcome(
                engine="lean",
                obligation_results=obligation_results,
                raw_output=output,
                verification_error=False,
                error_message="" if verified else output[:400],
            )
        except Exception as exc:
            return VerificationOutcome(
                engine="lean",
                obligation_results=self._all_failed(obligations, str(exc)),
                raw_output="",
                verification_error=True,
                error_message=str(exc),
            )
        finally:
            if file_path.exists():
                file_path.unlink()

    def _resolve_project_dir(self) -> Path:
        if self.project_dir:
            return Path(self.project_dir)
        candidate = Path(__file__).resolve().parents[3] / "lean_project"
        if candidate.exists():
            return candidate
        return Path(tempfile.gettempdir())

    def _running_in_docker(self) -> bool:
        return Path("/.dockerenv").exists()

    def _allow_local(self) -> bool:
        return os.getenv("ARGUS_ALLOW_LOCAL_VERIFY", "false").lower() == "true"

    def _all_failed(self, obligations: List[Obligation], message: str) -> List[ObligationResult]:
        return [
            ObligationResult(obligation=item, verified=False, engine="lean", message=message)
            for item in obligations
        ]

