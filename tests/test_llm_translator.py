from src.core.llm_provider import LLMClient
from src.core.translator.llm_translator import LLMTranslator


class _FakeLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        assert "Python Code" in contents
        return "def translated : Int := 0"


class _EmptyLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        return ""


class _ExceptionLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        raise RuntimeError("API timeout")


def test_llm_translator_success() -> None:
    outcome = LLMTranslator(llm_client=_FakeLLMClient()).translate("def f(x): return x", [], [])
    assert outcome.success
    assert outcome.used_llm
    assert "translated" in outcome.code


def test_llm_translator_empty_response_returns_failure() -> None:
    outcome = LLMTranslator(llm_client=_EmptyLLMClient()).translate("def f(x): return x", [], [])
    assert not outcome.success
    assert outcome.used_llm
    assert "empty" in outcome.error.lower()


def test_llm_translator_exception_propagation_returns_failure() -> None:
    outcome = LLMTranslator(llm_client=_ExceptionLLMClient()).translate("def f(x): return x", [], [])
    assert not outcome.success
    assert outcome.used_llm
    assert "API timeout" in outcome.error
