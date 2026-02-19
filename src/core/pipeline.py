from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from .assumption_evidence import validate_assumptions
from .invariant_discovery import InvariantDiscovery
from .models import AssumedInput, Obligation, VerificationSummary, Verdict
from .obligation_policy import ObligationPolicy
from .repair import RepairEngine
from .reporter import FileReport
from .semantic_guard import run_semantic_guard
from .translator import ASTTranslator, DafnyTranslator, LLMTranslator
from .translator.base import TranslationOutcome
from .verdict import compute_verdict
from .verifier import DafnyVerifier, LeanVerifier, VerifierRouter


@dataclass
class PipelineConfig:
    model: str = "gemini-2.5-pro"
    max_repair_attempts: int = 3
    trace_root: str = ".argus-trace"
    allow_repair: bool = True
    require_docker_verify: bool = True


@dataclass
class PipelineResult:
    filename: str
    verdict: Verdict
    obligations: List[Obligation]
    assumptions: List[AssumedInput]
    engine: str
    message: str
    repaired_code: str | None = None


class ArgusPipeline:
    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.policy = ObligationPolicy()
        self.discovery = InvariantDiscovery(model=self.config.model, use_llm=True)
        self.repair = RepairEngine(
            model=self.config.model,
            max_attempts=self.config.max_repair_attempts,
        )
        self.ast_translator = ASTTranslator()
        self.llm_translator = LLMTranslator(model=self.config.model)
        self.dafny_translator = DafnyTranslator()
        self.lean_verifier = LeanVerifier(require_docker=self.config.require_docker_verify)
        self.dafny_verifier = DafnyVerifier(require_docker=self.config.require_docker_verify)
        self.router = VerifierRouter(self.lean_verifier, self.dafny_verifier)
        self.last_run_id: str | None = None

    def run_file(self, filename: str, python_code: str) -> PipelineResult:
        run_id = self._new_run_id()
        self.last_run_id = run_id
        self._write_manifest(run_id=run_id, filenames=[filename], mode="single")
        result = self._run_file(
            filename=filename,
            python_code=python_code,
            allow_repair=self.config.allow_repair,
            run_id=run_id,
        )
        self._write_summary(run_id=run_id, results=[result])
        return result

    def _run_file(
        self,
        filename: str,
        python_code: str,
        allow_repair: bool,
        run_id: str,
    ) -> PipelineResult:
        trace_dir = Path(self.config.trace_root) / run_id / "files" / filename
        trace_dir.mkdir(parents=True, exist_ok=True)

        def finalize(result: PipelineResult) -> PipelineResult:
            self._write_json(
                trace_dir / "result.json",
                {
                    "filename": result.filename,
                    "verdict": result.verdict.value,
                    "engine": result.engine,
                    "message": result.message,
                    "obligations": [o.to_dict() for o in result.obligations],
                    "assumptions": [a.to_dict() for a in result.assumptions],
                    "repaired": bool(result.repaired_code),
                },
            )
            return result

        policy = self.policy.derive(python_code)
        discovery = self.discovery.discover(python_code)
        assumptions_valid, issues = validate_assumptions(discovery.assumed_inputs)

        self._write_json(
            trace_dir / "01_discovery.json",
            {
                "obligations": [o.to_dict() for o in policy.obligations],
                "assumed_inputs": [a.to_dict() for a in discovery.assumed_inputs],
                "assumptions_valid": assumptions_valid,
                "assumption_issues": [issue.reason for issue in issues],
                "unsupported_constructs": policy.unsupported_constructs,
                "llm_candidates_raw": discovery.llm_candidates_raw,
            },
        )

        if policy.unsupported_constructs:
            summary = VerificationSummary(
                obligation_results=[],
                assumptions_valid=assumptions_valid,
                unsupported_constructs=policy.unsupported_constructs,
                semantic_guard_passed=False,
            )
            decision = compute_verdict(summary)
            return finalize(
                PipelineResult(
                    filename=filename,
                    verdict=decision.verdict,
                    obligations=policy.obligations,
                    assumptions=discovery.assumed_inputs,
                    engine="n/a",
                    message=decision.reason,
                )
            )

        translation = self._translate(python_code, policy.obligations, discovery.assumed_inputs)
        self._write_text(
            trace_dir / ("02_translation.lean" if translation.language == "lean" else "02_translation.dfy"),
            translation.code if translation.success else translation.error,
        )
        if not translation.success:
            summary = VerificationSummary(
                obligation_results=[],
                assumptions_valid=assumptions_valid,
                unsupported_constructs=[],
                semantic_guard_passed=False,
                verification_error=True,
            )
            decision = compute_verdict(summary)
            return finalize(
                PipelineResult(
                    filename=filename,
                    verdict=decision.verdict,
                    obligations=policy.obligations,
                    assumptions=discovery.assumed_inputs,
                    engine=translation.language,
                    message=translation.error,
                )
            )

        guard = run_semantic_guard(python_code, translation.code, policy.obligations)
        self._write_json(
            trace_dir / "02_semantic_guard.json",
            {
                "passed": guard.passed,
                "issues": [{"code": issue.code, "message": issue.message} for issue in guard.issues],
            },
        )
        engine_selection = self.router.select_engine(python_code)
        verification = (
            self.lean_verifier.verify(translation.code, policy.obligations)
            if engine_selection.engine == "lean"
            else self.dafny_verifier.verify(translation.code, policy.obligations)
        )

        self._write_text(trace_dir / "03_verify_stdout.txt", verification.raw_output or verification.error_message)
        summary = VerificationSummary(
            obligation_results=verification.obligation_results,
            assumptions_valid=assumptions_valid,
            unsupported_constructs=[],
            semantic_guard_passed=guard.passed,
            verification_error=verification.verification_error,
            repaired=False,
        )
        decision = compute_verdict(summary)

        repaired_code: str | None = None
        if decision.verdict == Verdict.VULNERABLE and allow_repair and not verification.verification_error:
            repair_result = self.repair.repair(
                python_code=python_code,
                error_message=verification.error_message or verification.raw_output,
                obligations=policy.obligations,
            )
            if repair_result.success and repair_result.fixed_code:
                repaired_code = repair_result.fixed_code
                self._write_text(trace_dir / "04_repair_0.py", repaired_code)
                summary.repaired = True
                rerun = self._run_file(
                    filename=f"{filename}_repaired",
                    python_code=repaired_code,
                    allow_repair=False,
                    run_id=run_id,
                )
                if rerun.verdict in {Verdict.VERIFIED, Verdict.FIXED}:
                    return finalize(
                        PipelineResult(
                            filename=filename,
                            verdict=Verdict.FIXED,
                            obligations=policy.obligations,
                            assumptions=discovery.assumed_inputs,
                            engine=rerun.engine,
                            message="Repaired and verified",
                            repaired_code=repaired_code,
                        )
                    )

        return finalize(
            PipelineResult(
                filename=filename,
                verdict=decision.verdict,
                obligations=policy.obligations,
                assumptions=discovery.assumed_inputs,
                engine=engine_selection.engine,
                message=decision.reason if decision.reason else verification.error_message,
                repaired_code=repaired_code,
            )
        )

    def run_many(self, files: List[tuple[str, str]]) -> List[FileReport]:
        run_id = self._new_run_id()
        self.last_run_id = run_id
        self._write_manifest(run_id=run_id, filenames=[name for name, _ in files], mode="batch")

        results: List[PipelineResult] = []
        for filename, code in files:
            results.append(
                self._run_file(
                    filename=filename,
                    python_code=code,
                    allow_repair=self.config.allow_repair,
                    run_id=run_id,
                )
            )
        self._write_summary(run_id=run_id, results=results)

        reports: List[FileReport] = []
        for result in results:
            reports.append(
                FileReport(
                    filename=result.filename,
                    verdict=result.verdict,
                    obligations=result.obligations,
                    assumptions=result.assumptions,
                    engine=result.engine,
                    message=result.message,
                )
            )
        return reports

    def _translate(
        self,
        python_code: str,
        obligations: List[Obligation],
        assumptions: List[AssumedInput],
    ) -> TranslationOutcome:
        selection = self.router.select_engine(python_code)
        if selection.engine == "dafny":
            return self.dafny_translator.translate(python_code, obligations, assumptions)

        ast_outcome = self.ast_translator.translate(python_code, obligations, assumptions)
        if ast_outcome.success:
            return ast_outcome
        return self.llm_translator.translate(python_code, obligations, assumptions)

    def _write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, path: Path, content: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, indent=2), encoding="utf-8")

    def _new_run_id(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%fZ")

    def _write_manifest(self, run_id: str, filenames: List[str], mode: str) -> None:
        manifest = {
            "run_id": run_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "mode": mode,
            "files": filenames,
            "config": {
                "model": self.config.model,
                "max_repair_attempts": self.config.max_repair_attempts,
                "allow_repair": self.config.allow_repair,
                "require_docker_verify": self.config.require_docker_verify,
            },
        }
        self._write_json(Path(self.config.trace_root) / run_id / "manifest.json", manifest)

    def _write_summary(self, run_id: str, results: List[PipelineResult]) -> None:
        summary = {
            "run_id": run_id,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": len(results),
                "verified": sum(1 for item in results if item.verdict == Verdict.VERIFIED),
                "fixed": sum(1 for item in results if item.verdict == Verdict.FIXED),
                "vulnerable": sum(1 for item in results if item.verdict == Verdict.VULNERABLE),
                "unverified": sum(1 for item in results if item.verdict == Verdict.UNVERIFIED),
                "error": sum(1 for item in results if item.verdict == Verdict.ERROR),
            },
            "files": [
                {
                    "filename": item.filename,
                    "verdict": item.verdict.value,
                    "engine": item.engine,
                    "message": item.message,
                }
                for item in results
            ],
        }
        self._write_json(Path(self.config.trace_root) / run_id / "summary.json", summary)
