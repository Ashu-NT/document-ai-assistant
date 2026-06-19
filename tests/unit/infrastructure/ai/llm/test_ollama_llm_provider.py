import pytest

from src.infrastructure.ai.llm import OllamaLLMProvider
from src.shared.exceptions import LLMProviderError


class FakeOllamaResponse:
    def __init__(self, response: str | None) -> None:
        self.response = response


class FakeOllamaClient:
    def __init__(self, response) -> None:
        self.response = response
        self.calls = []

    def generate(self, *, model: str, prompt: str):
        self.calls.append(
            {
                "model": model,
                "prompt": prompt,
            }
        )
        return self.response


class FailingOllamaClient:
    def generate(self, *, model: str, prompt: str):
        raise RuntimeError("ollama failed")


def test_generate_calls_ollama_client_with_default_model() -> None:
    client = FakeOllamaClient(FakeOllamaResponse("  Generated maintenance steps.  "))
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )

    result = provider.generate("Summarize this maintenance section.")

    assert result == "Generated maintenance steps."
    assert client.calls == [
        {
            "model": "qwen3:8b",
            "prompt": "Summarize this maintenance section.",
        }
    ]


def test_generate_allows_model_override() -> None:
    client = FakeOllamaClient({"response": "Manual summary"})
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )

    result = provider.generate(
        "Summarize this maintenance section.",
        model="llama3.1:8b",
    )

    assert result == "Manual summary"
    assert client.calls == [
        {
            "model": "llama3.1:8b",
            "prompt": "Summarize this maintenance section.",
        }
    ]


def test_generate_raises_for_invalid_response_shape() -> None:
    client = FakeOllamaClient({})
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )

    with pytest.raises(LLMProviderError):
        provider.generate("Summarize this maintenance section.")


def test_generate_wraps_underlying_errors() -> None:
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=FailingOllamaClient(),
    )

    with pytest.raises(LLMProviderError):
        provider.generate("Summarize this maintenance section.")
