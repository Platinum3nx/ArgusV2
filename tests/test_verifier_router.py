from src.core.verifier import DafnyVerifier, LeanVerifier, VerifierRouter


def test_router_selects_dafny_for_loops() -> None:
    router = VerifierRouter(lean=LeanVerifier(require_docker=False), dafny=DafnyVerifier(require_docker=False))
    selection = router.select_engine(
        "def total(xs):\n    s = 0\n    for x in xs:\n        s += x\n    return s\n"
    )
    assert selection.engine == "dafny"


def test_router_selects_lean_for_non_loops() -> None:
    router = VerifierRouter(lean=LeanVerifier(require_docker=False), dafny=DafnyVerifier(require_docker=False))
    selection = router.select_engine("def f(x):\n    return x + 1\n")
    assert selection.engine == "lean"

