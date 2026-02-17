from src.core.translator.llm_translator import LLMTranslator


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeModels:
    def generate_content(self, model: str, contents: str) -> _FakeResponse:
        assert model == "gemini-2.5-pro"
        assert "Python Code" in contents
        return _FakeResponse("def translated : Int := 0")


class _FakeClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.models = _FakeModels()


def test_llm_translator_success(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setattr("src.core.translator.llm_translator.genai.Client", _FakeClient)

    outcome = LLMTranslator().translate("def f(x): return x", [], [])
    assert outcome.success
    assert outcome.used_llm
    assert "translated" in outcome.code

