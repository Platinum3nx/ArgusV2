from types import SimpleNamespace

from src.core.llm_provider import LLMClient
from src.core.models import ObligationResult, Verdict
from src.core.pipeline import ArgusPipeline, PipelineConfig
from src.core.proof_search import ProofSearchResult
from src.core.verifier.base import VerificationOutcome


class _FakeLLMClient(LLMClient):
    """Minimal LLM client for pipeline tests — returns empty string (graceful no-op)."""

    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        return ""


def test_pipeline_verified_path(monkeypatch, tmp_path) -> None:
    def _fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("src.core.verifier.lean_verifier.subprocess.run", _fake_run)
    monkeypatch.setenv("ARGUS_ALLOW_LOCAL_VERIFY", "true")

    config = PipelineConfig(
        allow_repair=False,
        require_docker_verify=False,
        trace_root=str(tmp_path / ".argus-trace"),
    )
    pipeline = ArgusPipeline(config=config, llm_client=_FakeLLMClient())
    result = pipeline.run_file(
        filename="withdraw.py",
        python_code="def withdraw(balance: int, amount: int) -> int:\n    return balance - amount\n",
    )
    assert result.verdict in {Verdict.VERIFIED, Verdict.FIXED}
    assert result.engine == "lean"


def test_pipeline_unverified_on_unsupported_construct(tmp_path) -> None:
    config = PipelineConfig(
        allow_repair=False,
        require_docker_verify=False,
        trace_root=str(tmp_path / ".argus-trace"),
    )
    pipeline = ArgusPipeline(config=config, llm_client=_FakeLLMClient())
    result = pipeline.run_file(
        filename="worker.py",
        python_code="async def worker():\n    return 1\n",
    )
    assert result.verdict == Verdict.UNVERIFIED


def test_pipeline_accepts_verified_proof_search_candidate(tmp_path) -> None:
    config = PipelineConfig(
        allow_repair=False,
        allow_proof_search=True,
        require_docker_verify=False,
        trace_root=str(tmp_path / ".argus-trace"),
    )
    pipeline = ArgusPipeline(config=config, llm_client=_FakeLLMClient())

    def _fake_verify(proof_code: str, obligations):
        verified = "\n  linarith" in proof_code and "try linarith" not in proof_code
        return VerificationOutcome(
            engine="lean",
            obligation_results=[
                ObligationResult(
                    obligation=item,
                    verified=verified,
                    engine="lean",
                    message="" if verified else "failed",
                )
                for item in obligations
            ],
            raw_output="ok" if verified else "failed",
            verification_error=False,
            error_message="" if verified else "failed",
        )

    pipeline.lean_verifier.verify = _fake_verify
    pipeline.proof_search.search = lambda **kwargs: ProofSearchResult(
        success=True,
        proof_code=kwargs["lean_code"].replace("try linarith", "linarith"),
        attempts=[],
    )

    result = pipeline.run_file(
        filename="withdraw.py",
        python_code="def withdraw(balance: int, amount: int) -> int:\n    return balance - amount\n",
    )
    assert result.verdict == Verdict.VERIFIED
    assert "proof search" in result.message.lower()
