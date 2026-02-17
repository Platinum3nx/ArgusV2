from types import SimpleNamespace

from src.core.models import Obligation
from src.core.verifier.dafny_verifier import DafnyVerifier


def test_dafny_verifier_success(monkeypatch) -> None:
    def _fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="Dafny verified, 0 errors", stderr="")

    monkeypatch.setattr("src.core.verifier.dafny_verifier.subprocess.run", _fake_run)

    obligations = [
        Obligation(
            id="f:loop_progress_and_safety",
            property="loop safe",
            category="loop_invariant",
            description="loop",
        )
    ]
    verifier = DafnyVerifier(require_docker=False)
    outcome = verifier.verify("method F() returns (result:int) { result := 0; }", obligations)
    assert outcome.all_passed
    assert not outcome.verification_error

