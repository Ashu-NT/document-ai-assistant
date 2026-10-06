import logging

import pytest

from src.infrastructure.ai.llm import OllamaLLMProvider
from src.shared.exceptions import LLMProviderError


class FakeOllamaResponse:
    def __init__(self, response: str | None) -> None:
        self.response = response


class FakeOllamaResponseWithMetadata:
    """A richer fake mirroring Ollama's real /api/generate response shape
    (an object with attributes, not a dict) - used to exercise
    generate_with_metadata()'s mapping without depending on the real
    ollama package's response class."""

    def __init__(self, **fields) -> None:
        for key, value in fields.items():
            setattr(self, key, value)


class FakeOllamaResponseModel:
    """A pydantic-model-shaped fake (has .model_dump()) - exercises the
    other branch of OllamaLLMProvider._as_dict()."""

    def __init__(self, **fields) -> None:
        self._fields = fields
        self.response = fields.get("response")

    def model_dump(self) -> dict:
        return dict(self._fields)


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


# -- generate_with_metadata(): provider-neutral LLMGenerationResult --


def test_generate_with_metadata_maps_native_ollama_fields() -> None:
    client = FakeOllamaClient(
        FakeOllamaResponseWithMetadata(
            response="  Generated maintenance steps.  ",
            model="qwen2.5:3b",
            created_at="2026-10-06T03:52:21Z",
            done=True,
            done_reason="stop",
            context=[1, 2, 3, 4, 5],
            total_duration=11478187000,
            load_duration=5975917900,
            prompt_eval_count=2050,
            prompt_eval_duration=827971000,
            eval_count=354,
            eval_duration=4635693000,
        )
    )
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=client,
    )

    result = provider.generate_with_metadata("Summarize this maintenance section.")

    assert result.text == "Generated maintenance steps."
    assert result.provider_name == "ollama"
    assert result.model == "qwen2.5:3b"
    assert result.done is True
    assert result.finish_reason == "stop"
    assert result.prompt_tokens == 2050
    assert result.completion_tokens == 354
    assert result.total_duration_ns == 11478187000
    assert result.prompt_duration_ns == 827971000
    assert result.completion_duration_ns == 4635693000


def test_generate_with_metadata_never_retains_the_raw_context_token_array() -> None:
    client = FakeOllamaClient(
        FakeOllamaResponseWithMetadata(
            response="ok",
            done=True,
            done_reason="stop",
            context=list(range(50_000)),  # a large provider payload
        )
    )
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=client,
    )

    result = provider.generate_with_metadata("Summarize this maintenance section.")

    assert "context" not in result.provider_metadata
    assert all(
        not isinstance(value, list) or len(value) < 100
        for value in result.provider_metadata.values()
    )


def test_generate_with_metadata_keeps_unpromoted_fields_in_provider_metadata() -> None:
    client = FakeOllamaClient(
        FakeOllamaResponseWithMetadata(
            response="ok",
            done=True,
            done_reason="stop",
            created_at="2026-10-06T03:52:21Z",
            load_duration=5975917900,
        )
    )
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=client,
    )

    result = provider.generate_with_metadata("Summarize this maintenance section.")

    assert result.provider_metadata["created_at"] == "2026-10-06T03:52:21Z"
    assert result.provider_metadata["load_duration"] == 5975917900
    # promoted fields must not be duplicated into provider_metadata
    assert "done" not in result.provider_metadata
    assert "done_reason" not in result.provider_metadata
    assert "response" not in result.provider_metadata


def test_generate_with_metadata_handles_missing_optional_fields_safely() -> None:
    client = FakeOllamaClient(FakeOllamaResponse("Generated maintenance steps."))
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=client,
    )

    result = provider.generate_with_metadata("Summarize this maintenance section.")

    assert result.text == "Generated maintenance steps."
    assert result.provider_name == "ollama"
    assert result.done is None
    assert result.finish_reason is None
    assert result.prompt_tokens is None
    assert result.completion_tokens is None
    assert result.total_duration_ns is None
    assert result.prompt_duration_ns is None
    assert result.completion_duration_ns is None
    assert result.provider_metadata == {}


def test_generate_with_metadata_handles_dict_shaped_response() -> None:
    client = FakeOllamaClient(
        {
            "response": "Generated maintenance steps.",
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 10,
            "eval_count": 5,
        }
    )
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=client,
    )

    result = provider.generate_with_metadata("Summarize this maintenance section.")

    assert result.text == "Generated maintenance steps."
    assert result.done is True
    assert result.finish_reason == "stop"
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5


def test_generate_with_metadata_handles_pydantic_model_shaped_response() -> None:
    client = FakeOllamaClient(
        FakeOllamaResponseModel(
            response="Generated maintenance steps.",
            model="qwen2.5:3b",
            done=True,
            done_reason="stop",
            prompt_eval_count=10,
            eval_count=5,
            context=[1, 2, 3],
        )
    )
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=client,
    )

    result = provider.generate_with_metadata("Summarize this maintenance section.")

    assert result.text == "Generated maintenance steps."
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5
    assert "context" not in result.provider_metadata


def test_generate_with_metadata_raises_for_invalid_response_shape() -> None:
    client = FakeOllamaClient({})
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=client,
    )

    with pytest.raises(LLMProviderError):
        provider.generate_with_metadata("Summarize this maintenance section.")


def test_generate_with_metadata_wraps_underlying_errors() -> None:
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=FailingOllamaClient(),
    )

    with pytest.raises(LLMProviderError):
        provider.generate_with_metadata("Summarize this maintenance section.")


def test_generate_with_metadata_passes_the_same_request_shape_as_generate() -> None:
    """generate_with_metadata() must send the client call exactly like
    generate() does - same model/format/options forwarding, unchanged."""
    client = FakeOllamaClient(FakeOllamaResponse("{}"))
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen3:8b",
        client=client,
    )
    schema = {"type": "object", "properties": {"identifiers": {"type": "array"}}}

    provider.generate_with_metadata(
        "Extract structured data.",
        model="llama3.1:8b",
        temperature=0.0,
        response_schema=schema,
        num_ctx=8192,
    )

    assert client.calls == [
        {
            "model": "llama3.1:8b",
            "prompt": "Extract structured data.",
            "format": schema,
            "options": {"temperature": 0.0, "num_ctx": 8192},
        }
    ]


def test_generate_text_is_unaffected_by_generate_with_metadata_existing() -> None:
    """Regression guard: generate() must keep returning exactly the same
    stripped string it always did, unaffected by the new sibling method
    sharing its internals."""
    client = FakeOllamaClient(
        FakeOllamaResponseWithMetadata(
            response="  Generated maintenance steps.  ",
            done=True,
            done_reason="stop",
            prompt_eval_count=10,
            eval_count=5,
        )
    )
    provider = OllamaLLMProvider(
        base_url="http://localhost:11434",
        default_model="qwen2.5:3b",
        client=client,
    )

    assert provider.generate("Summarize this maintenance section.") == (
        "Generated maintenance steps."
    )
