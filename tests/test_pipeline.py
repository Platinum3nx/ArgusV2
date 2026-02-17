from types import SimpleNamespace

from src.core.pipeline import ArgusPipeline, PipelineConfig
from src.core.models import Verdict


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
    pipeline = ArgusPipeline(config=config)
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
    pipeline = ArgusPipeline(config=config)
    result = pipeline.run_file(
        filename="worker.py",
        python_code="async def worker():\n    return 1\n",
    )
    assert result.verdict == Verdict.UNVERIFIED

