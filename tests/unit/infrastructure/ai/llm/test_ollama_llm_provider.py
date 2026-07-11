import logging

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


def test_generate_response_schema_overrides_json_mode() -> None:
    client = FakeOllamaClient(FakeOllamaResponse("{}"))
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )
    schema = {"type": "object", "properties": {"identifiers": {"type": "array"}}}

    provider.generate(
        "Extract structured data.",
        json_mode=True,
        response_schema=schema,
    )

    assert client.calls == [
        {
            "model": "qwen3:8b",
            "prompt": "Extract structured data.",
            "format": schema,
        }
    ]


def test_generate_passes_num_ctx_alongside_temperature() -> None:
    client = FakeOllamaClient(FakeOllamaResponse("{}"))
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )

    provider.generate(
        "Answer the question.",
        temperature=0.2,
        num_ctx=8192,
    )

    assert client.calls == [
        {
            "model": "qwen3:8b",
            "prompt": "Answer the question.",
            "options": {"temperature": 0.2, "num_ctx": 8192},
        }
    ]


def test_generate_omits_options_when_temperature_and_num_ctx_both_missing() -> None:
    client = FakeOllamaClient(FakeOllamaResponse("{}"))
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )

    provider.generate("Answer the question.")

    assert client.calls == [
        {
            "model": "qwen3:8b",
            "prompt": "Answer the question.",
        }
    ]


# -- finding 3.7: settings-load failure logs a warning before falling back -


def test_default_ollama_base_url_logs_warning_on_settings_failure(monkeypatch, caplog) -> None:
    from src.infrastructure.ai.llm.ollama_llm_provider import (
        DEFAULT_OLLAMA_BASE_URL,
        _default_ollama_base_url,
    )

    monkeypatch.setattr("src.config.settings.llm_settings", object())

    with caplog.at_level(logging.WARNING):
        result = _default_ollama_base_url()

    assert result == DEFAULT_OLLAMA_BASE_URL
    assert any(
        "settings_fallback" in message and "ollama_base_url" in message
        for message in caplog.messages
    )


def test_default_ollama_model_logs_warning_on_settings_failure(monkeypatch, caplog) -> None:
    from src.infrastructure.ai.llm.ollama_llm_provider import (
        DEFAULT_OLLAMA_MODEL,
        _default_ollama_model,
    )

    monkeypatch.setattr("src.config.settings.llm_settings", object())

    with caplog.at_level(logging.WARNING):
        result = _default_ollama_model()

    assert result == DEFAULT_OLLAMA_MODEL
    assert any(
        "settings_fallback" in message and "general_llm" in message
        for message in caplog.messages
    )
