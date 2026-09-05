import pytest
from pydantic import ValidationError

from src.config.settings.ingestion_settings import IngestionSettings


def test_max_generated_questions_per_chunk_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("MAX_GENERATED_QUESTIONS_PER_CHUNK", "7")

    settings = IngestionSettings()

    assert settings.max_generated_questions_per_chunk == 7


def test_max_generated_questions_per_chunk_must_be_positive(monkeypatch) -> None:
    monkeypatch.setenv("MAX_GENERATED_QUESTIONS_PER_CHUNK", "0")

    with pytest.raises(ValidationError):
        IngestionSettings()
