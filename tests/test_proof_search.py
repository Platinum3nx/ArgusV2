from src.core.llm_provider import LLMClient
from src.core.proof_search import ProofSearchEngine


class _FakeLLMClient(LLMClient):
    """Returns empty string — simulates empty response scenario."""
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        return ""


class _ExceptionLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        raise RuntimeError("API timeout")


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
    ok, reason = ProofSearchEngine(llm_client=_FakeLLMClient()).validate_candidate(original, candidate)
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
    ok, reason = ProofSearchEngine(llm_client=_FakeLLMClient()).validate_candidate(original, candidate)
    assert not ok
    assert "header/goal" in reason


def test_validate_candidate_allows_sorry_in_comments() -> None:
    """A1.6: 'sorry' inside a Lean comment should NOT trigger rejection."""
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
  -- sorry about this naming convention
  unfold f
  omega
"""
    ok, reason = ProofSearchEngine(llm_client=_FakeLLMClient()).validate_candidate(original, candidate)
    assert ok, f"Should accept sorry in comment, got: {reason}"


def test_validate_candidate_rejects_sorry_in_code() -> None:
    """A1.6: 'sorry' as an actual tactic must still be rejected."""
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
    ok, reason = ProofSearchEngine(llm_client=_FakeLLMClient()).validate_candidate(original, candidate)
    assert not ok
    assert "forbidden" in reason


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
    ok, reason = ProofSearchEngine(llm_client=_FakeLLMClient()).validate_candidate(original, candidate)
    assert not ok
    assert "forbidden" in reason


def test_proof_search_empty_response_returns_no_proof() -> None:
    engine = ProofSearchEngine(llm_client=_FakeLLMClient(), max_attempts=1)
    result = engine.search(
        lean_code="theorem f : True := by trivial",
        obligations=[],
        verifier_error="proof failed",
    )
    assert not result.success
    assert result.proof_code is None


def test_proof_search_exception_propagation_returns_no_proof() -> None:
    engine = ProofSearchEngine(llm_client=_ExceptionLLMClient(), max_attempts=1)
    result = engine.search(
        lean_code="theorem f : True := by trivial",
        obligations=[],
        verifier_error="proof failed",
    )
    assert not result.success
    assert result.proof_code is None
