from __future__ import annotations

from dataclasses import dataclass

from src.config.settings import classification_settings, llm_settings


@dataclass(frozen=True)
class ClassificationRuntimeSettings:
    document_classification_model: str | None
    chunk_type_classification_enabled: bool
    chunk_type_classification_model: str | None


def resolve_classification_runtime_settings() -> ClassificationRuntimeSettings:
    return ClassificationRuntimeSettings(
        document_classification_model=(
            classification_settings.classification_llm
            or llm_settings.classification_llm
            or llm_settings.general_llm
        ),
        chunk_type_classification_enabled=(
            classification_settings.chunk_type_classification_enabled
        ),
        chunk_type_classification_model=(
            classification_settings.chunk_classification_llm
            or llm_settings.classification_llm
            or llm_settings.general_llm
        ),
    )
