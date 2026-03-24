from src.core.llm_provider import LLMClient
from src.core.translator.llm_translator import LLMTranslator


class _FakeLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        assert "Python Code" in contents
        return "```lean\nimport Mathlib.Tactic.Linarith\n\ndef translated : Int := 0\n```"


class _WrappedLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        assert "Obligations" in contents
        return (
            "Here is the Lean file you asked for.\n\n"
            "```lean4\n"
            "import Mathlib.Tactic.SplitIfs\n\n"
            "theorem translated : True := by\n"
            "  trivial\n"
            "```\n\n"
            "The proof is complete."
        )


class _EmptyLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        return ""


class _NoCodeLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        return "This is not Lean code."


class _ExceptionLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        raise RuntimeError("API timeout")


def test_llm_translator_success() -> None:
    outcome = LLMTranslator(llm_client=_FakeLLMClient()).translate("def f(x): return x", [], [])
    assert outcome.success
    assert outcome.used_llm
    assert outcome.code.startswith("import Mathlib.Tactic.Linarith")
    assert "```" not in outcome.code


def test_llm_translator_strips_wrappers_and_keeps_lean_block() -> None:
    outcome = LLMTranslator(llm_client=_WrappedLLMClient()).translate("def f(x): return x", [], [])
    assert outcome.success
    assert outcome.used_llm
    assert outcome.code.startswith("import Mathlib.Tactic.SplitIfs")
    assert outcome.code.endswith("trivial")
    assert "Here is the Lean file" not in outcome.code
    assert "```" not in outcome.code


def test_llm_translator_empty_response_returns_failure() -> None:
    outcome = LLMTranslator(llm_client=_EmptyLLMClient()).translate("def f(x): return x", [], [])
    assert not outcome.success
    assert outcome.used_llm
    assert "empty" in outcome.error.lower()


def test_llm_translator_non_code_response_returns_failure() -> None:
    outcome = LLMTranslator(llm_client=_NoCodeLLMClient()).translate("def f(x): return x", [], [])
    assert not outcome.success
    assert outcome.used_llm
    assert "no usable lean code" in outcome.error.lower()


def test_llm_translator_exception_propagation_returns_failure() -> None:
    outcome = LLMTranslator(llm_client=_ExceptionLLMClient()).translate("def f(x): return x", [], [])
    assert not outcome.success
    assert outcome.used_llm
    assert "API timeout" in outcome.error
