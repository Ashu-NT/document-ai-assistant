import pytest

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
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "temperature": temperature,
                "json_mode": json_mode,
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
        }
    ]
