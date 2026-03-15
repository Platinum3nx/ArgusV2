from src.core.llm_provider import LLMClient
from src.core.translator.llm_translator import LLMTranslator


class _FakeLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        assert "Python Code" in contents
        return "def translated : Int := 0"


def test_llm_translator_success() -> None:
    outcome = LLMTranslator(llm_client=_FakeLLMClient()).translate("def f(x): return x", [], [])
    assert outcome.success
    assert outcome.used_llm
    assert "translated" in outcome.code
