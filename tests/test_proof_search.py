from src.core.proof_search import ProofSearchEngine


def test_validate_candidate_accepts_proof_body_changes_only() -> None:
    original = """
def f (x : Int) : Int :=
  x + 1

theorem f_nonneg (x : Int) : (f x >= 0) := by
  unfold f
  omega
"""
    candidate = """
def f (x : Int) : Int :=
  x + 1

theorem f_nonneg (x : Int) : (f x >= 0) := by
  unfold f
  linarith
"""
    ok, reason = ProofSearchEngine().validate_candidate(original, candidate)
    assert ok
    assert "preserved" in reason


def test_validate_candidate_rejects_theorem_goal_mutation() -> None:
    original = """
def f (x : Int) : Int :=
  x + 1

theorem f_nonneg (x : Int) : (f x >= 0) := by
  unfold f
  omega
"""
    candidate = """
def f (x : Int) : Int :=
  x + 1

theorem f_nonneg (x : Int) : True := by
  trivial
"""
    ok, reason = ProofSearchEngine().validate_candidate(original, candidate)
    assert not ok
    assert "header/goal" in reason


def test_validate_candidate_rejects_proof_bypass_markers() -> None:
    original = """
def f (x : Int) : Int :=
  x + 1

theorem f_nonneg (x : Int) : (f x >= 0) := by
  unfold f
  omega
"""
    candidate = """
def f (x : Int) : Int :=
  x + 1

theorem f_nonneg (x : Int) : (f x >= 0) := by
  sorry
"""
    ok, reason = ProofSearchEngine().validate_candidate(original, candidate)
    assert not ok
    assert "forbidden" in reason
