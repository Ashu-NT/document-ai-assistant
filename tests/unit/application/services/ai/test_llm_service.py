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
