from types import SimpleNamespace

from src.core.models import Obligation
from src.core.verifier.lean_verifier import LeanVerifier


def test_lean_verifier_success(monkeypatch, tmp_path) -> None:
    def _fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("src.core.verifier.lean_verifier.subprocess.run", _fake_run)

    obligations = [
        Obligation(
            id="f:non_negative_result",
            property="f(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    verifier = LeanVerifier(project_dir=str(tmp_path), require_docker=False)
    outcome = verifier.verify("def f (x : Int) : Int := x", obligations)
    assert not outcome.verification_error
    assert outcome.all_passed


def test_lean_verifier_fails_if_docker_required(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("ARGUS_ALLOW_LOCAL_VERIFY", raising=False)
    obligations = [
        Obligation(
            id="f:non_negative_result",
            property="f(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    verifier = LeanVerifier(project_dir=str(tmp_path), require_docker=True)
    outcome = verifier.verify("def f (x : Int) : Int := x", obligations)
    assert outcome.verification_error
    assert not outcome.all_passed

