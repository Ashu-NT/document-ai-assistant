import pytest
from pydantic import ValidationError

from src.config.settings.classification_settings import ClassificationSettings


def test_chunk_classification_confidence_threshold_reads_environment(
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHUNK_CLASSIFICATION_CONFIDENCE_THRESHOLD", "0.82")

    settings = ClassificationSettings()

    assert settings.chunk_classification_confidence_threshold == 0.82


def test_chunk_classification_confidence_threshold_must_be_probability(
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHUNK_CLASSIFICATION_CONFIDENCE_THRESHOLD", "1.1")

    with pytest.raises(ValidationError):
        ClassificationSettings()
