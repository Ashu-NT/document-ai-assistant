import pytest

from src.application.contracts.ai import LLMGenerationResult
from src.application.services.ai import LLMService
from src.shared.exceptions import LLMProviderError


class FakeLLMProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, str | None]] = []

    def generate(self, prompt: str, model: str | None = None) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
            }
        )
        return "Generated maintenance steps."


class FailingLLMProvider:
    def generate(self, prompt: str, model: str | None = None) -> str:
        raise LLMProviderError("LLM provider failed.")


class FakeLLMProviderWithOptions:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "temperature": temperature,
                "json_mode": json_mode,
                "response_schema": response_schema,
            }
        )
        return "Generated maintenance steps."


def test_generate_calls_provider() -> None:
    provider = FakeLLMProvider()
    service = LLMService(provider)

    result = service.generate(
        "Summarize this maintenance section.",
        model="qwen3:8b",
    )

    assert result == "Generated maintenance steps."
    assert provider.calls == [
        {
            "prompt": "Summarize this maintenance section.",
            "model": "qwen3:8b",
        }
    ]


def test_generate_passes_through_none_model() -> None:
    provider = FakeLLMProvider()
    service = LLMService(provider)

    result = service.generate("Summarize this maintenance section.")

    assert result == "Generated maintenance steps."
    assert provider.calls == [
        {
            "prompt": "Summarize this maintenance section.",
            "model": None,
        }
    ]


def test_generate_does_not_swallow_errors() -> None:
    service = LLMService(FailingLLMProvider())

    with pytest.raises(LLMProviderError):
        service.generate("Summarize this maintenance section.")


def test_generate_does_not_forward_temperature_or_json_mode_by_default() -> None:
    provider = FakeLLMProvider()
    service = LLMService(provider)

    result = service.generate(
        "Summarize this maintenance section.",
        model="qwen3:8b",
    )

    assert result == "Generated maintenance steps."


def test_generate_forwards_temperature_and_json_mode_when_requested() -> None:
    provider = FakeLLMProviderWithOptions()
    service = LLMService(provider)

    service.generate(
        "Summarize this maintenance section.",
        model="qwen3:8b",
        temperature=0.0,
        json_mode=True,
    )

    assert provider.calls == [
        {
            "prompt": "Summarize this maintenance section.",
            "model": "qwen3:8b",
            "temperature": 0.0,
            "json_mode": True,
            "response_schema": None,
        }
    ]


class FakeLLMProviderWithMetadata:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate(self, prompt: str, model: str | None = None) -> str:
        return "Generated maintenance steps."

    def generate_with_metadata(
        self,
        prompt: str,
        model: str | None = None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict | None = None,
        num_ctx: int | None = None,
    ) -> LLMGenerationResult:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "temperature": temperature,
                "json_mode": json_mode,
                "response_schema": response_schema,
                "num_ctx": num_ctx,
            }
        )
        return LLMGenerationResult(
            text="Generated maintenance steps.",
            provider_name="fake",
            model=model,
            done=True,
            finish_reason="stop",
            prompt_tokens=10,
            completion_tokens=5,
        )


def test_generate_with_metadata_calls_provider_and_returns_its_result() -> None:
    provider = FakeLLMProviderWithMetadata()
    service = LLMService(provider)

    result = service.generate_with_metadata(
        "Summarize this maintenance section.",
        model="qwen3:8b",
        temperature=0.0,
    )

    assert result.text == "Generated maintenance steps."
    assert result.provider_name == "fake"
    assert result.done is True
    assert result.finish_reason == "stop"
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5
    assert provider.calls == [
        {
            "prompt": "Summarize this maintenance section.",
            "model": "qwen3:8b",
            "temperature": 0.0,
            "json_mode": False,
            "response_schema": None,
            "num_ctx": None,
        }
    ]


def test_generate_with_metadata_does_not_forward_unset_options() -> None:
    provider = FakeLLMProviderWithMetadata()
    service = LLMService(provider)

    service.generate_with_metadata("Summarize this maintenance section.")

    assert provider.calls == [
        {
            "prompt": "Summarize this maintenance section.",
            "model": None,
            "temperature": None,
            "json_mode": False,
            "response_schema": None,
            "num_ctx": None,
        }
    ]


def test_generate_is_unaffected_by_generate_with_metadata_existing() -> None:
    """Regression guard: plain generate() on a provider that ALSO
    implements generate_with_metadata() must still return exactly the bare
    string it always did."""
    provider = FakeLLMProviderWithMetadata()
    service = LLMService(provider)

    result = service.generate("Summarize this maintenance section.", model="qwen3:8b")

    assert result == "Generated maintenance steps."
    assert isinstance(result, str)


def test_generate_forwards_response_schema_when_requested() -> None:
    provider = FakeLLMProviderWithOptions()
    service = LLMService(provider)
    schema = {"type": "object", "properties": {"answer_text": {"type": "string"}}}

    service.generate(
        "Summarize this maintenance section.",
        model="qwen3:8b",
        response_schema=schema,
    )

    assert provider.calls == [
        {
            "prompt": "Summarize this maintenance section.",
            "model": "qwen3:8b",
            "temperature": None,
            "json_mode": False,
            "response_schema": schema,
        }
    ]
