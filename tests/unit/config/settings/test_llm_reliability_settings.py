import pytest
from pydantic import ValidationError

from src.config.settings.extraction_settings import ExtractionSettings
from src.config.settings.llm_settings import LLMSettings


def test_ollama_timeouts_read_environment(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_CONNECT_TIMEOUT_SECONDS", "5")
    monkeypatch.setenv("OLLAMA_READ_TIMEOUT_SECONDS", "300")
    monkeypatch.setenv("OLLAMA_WRITE_TIMEOUT_SECONDS", "7")
    monkeypatch.setenv("OLLAMA_POOL_TIMEOUT_SECONDS", "8")

    settings = LLMSettings()

    assert settings.ollama_connect_timeout_seconds == 5
    assert settings.ollama_read_timeout_seconds == 300
    assert settings.ollama_write_timeout_seconds == 7
    assert settings.ollama_pool_timeout_seconds == 8


@pytest.mark.parametrize(
    "field",
    [
        "OLLAMA_CONNECT_TIMEOUT_SECONDS",
        "OLLAMA_READ_TIMEOUT_SECONDS",
        "OLLAMA_WRITE_TIMEOUT_SECONDS",
        "OLLAMA_POOL_TIMEOUT_SECONDS",
        "OLLAMA_ANSWER_READ_TIMEOUT_SECONDS",
    ],
)
def test_ollama_timeouts_reject_non_positive_values(monkeypatch, field) -> None:
    monkeypatch.setenv(field, "0")

    with pytest.raises(ValidationError):
        LLMSettings()


@pytest.mark.parametrize(
    "field",
    [
        "OLLAMA_ANSWER_MAX_OUTPUT_TOKENS",
        "OLLAMA_QUESTION_GENERATION_MAX_OUTPUT_TOKENS",
        "OLLAMA_CLASSIFICATION_MAX_OUTPUT_TOKENS",
    ],
)
def test_ollama_output_token_settings_reject_non_positive_values(
    monkeypatch, field
) -> None:
    monkeypatch.setenv(field, "0")

    with pytest.raises(ValidationError):
        LLMSettings()


@pytest.mark.parametrize(
    "field",
    [
        "OLLAMA_ANSWER_MAX_OUTPUT_TOKENS",
        "OLLAMA_QUESTION_GENERATION_MAX_OUTPUT_TOKENS",
        "OLLAMA_CLASSIFICATION_MAX_OUTPUT_TOKENS",
    ],
)
def test_ollama_output_token_settings_reject_unreasonably_large_values(
    monkeypatch, field
) -> None:
    monkeypatch.setenv(field, "1000000")

    with pytest.raises(ValidationError):
        LLMSettings()


def test_extraction_output_token_settings_read_environment(monkeypatch) -> None:
    monkeypatch.setenv("EXTRACTION_MAX_OUTPUT_TOKENS", "2048")
    monkeypatch.setenv("EXTRACTION_CANDIDATE_ROUTER_MAX_OUTPUT_TOKENS", "128")

    settings = ExtractionSettings()

    assert settings.extraction_max_output_tokens == 2048
    assert settings.extraction_candidate_router_max_output_tokens == 128


@pytest.mark.parametrize(
    "field",
    ["EXTRACTION_MAX_OUTPUT_TOKENS", "EXTRACTION_CANDIDATE_ROUTER_MAX_OUTPUT_TOKENS"],
)
def test_extraction_output_token_settings_reject_non_positive_values(
    monkeypatch, field
) -> None:
    monkeypatch.setenv(field, "-1")

    with pytest.raises(ValidationError):
        ExtractionSettings()


def test_extraction_execution_budget_defaults_to_disabled(monkeypatch) -> None:
    monkeypatch.delenv("EXTRACTION_EXECUTION_BUDGET_SECONDS", raising=False)

    settings = ExtractionSettings()

    assert settings.extraction_execution_budget_seconds is None


def test_extraction_execution_budget_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("EXTRACTION_EXECUTION_BUDGET_SECONDS", "1800")

    settings = ExtractionSettings()

    assert settings.extraction_execution_budget_seconds == 1800


def test_extraction_execution_budget_rejects_non_positive_values(monkeypatch) -> None:
    monkeypatch.setenv("EXTRACTION_EXECUTION_BUDGET_SECONDS", "0")

    with pytest.raises(ValidationError):
        ExtractionSettings()


def test_extraction_num_ctx_defaults_to_8192(monkeypatch) -> None:
    monkeypatch.delenv("EXTRACTION_NUM_CTX", raising=False)

    settings = ExtractionSettings()

    assert settings.extraction_num_ctx == 8192


def test_extraction_num_ctx_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("EXTRACTION_NUM_CTX", "16384")

    settings = ExtractionSettings()

    assert settings.extraction_num_ctx == 16384


def test_extraction_num_ctx_rejects_non_positive_values(monkeypatch) -> None:
    monkeypatch.setenv("EXTRACTION_NUM_CTX", "0")

    with pytest.raises(ValidationError):
        ExtractionSettings()
