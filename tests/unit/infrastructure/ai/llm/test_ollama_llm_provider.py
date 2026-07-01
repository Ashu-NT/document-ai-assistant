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

    def generate(self, *, model: str, prompt: str, format=None, options=None):
        call = {"model": model, "prompt": prompt}
        if format is not None:
            call["format"] = format
        if options is not None:
            call["options"] = options
        self.calls.append(call)
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


def test_generate_omits_format_and_options_by_default() -> None:
    client = FakeOllamaClient(FakeOllamaResponse("Generated maintenance steps."))
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )

    provider.generate("Summarize this maintenance section.")

    assert client.calls == [
        {
            "model": "qwen3:8b",
            "prompt": "Summarize this maintenance section.",
        }
    ]


def test_generate_passes_json_mode_and_temperature_to_client() -> None:
    client = FakeOllamaClient(FakeOllamaResponse("{}"))
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )

    provider.generate(
        "Extract structured data.",
        temperature=0.0,
        json_mode=True,
    )

    assert client.calls == [
        {
            "model": "qwen3:8b",
            "prompt": "Extract structured data.",
            "format": "json",
            "options": {"temperature": 0.0},
        }
    ]
