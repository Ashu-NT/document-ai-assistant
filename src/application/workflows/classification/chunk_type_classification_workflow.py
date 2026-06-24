from typing import Callable

from src.application.workflows.parsing.builders.chunking.builders.chunk_type_llm_classifier import (
    ChunkTypeLLMClassifier,
)
from src.domain.common import ChunkType
from src.domain.document import DocumentChunk

_UNRESOLVED_TYPES = {ChunkType.GENERAL, ChunkType.UNKNOWN}

_CHUNK_TYPE_CLASSIFICATION_SOURCE = "llm"


def _default_chunk_type_classification_enabled() -> bool:
    try:
        from src.config.settings import classification_settings

        return classification_settings.chunk_type_classification_enabled
    except Exception:
        return False


def _default_classification_model() -> str | None:
    try:
        from src.config.settings import classification_settings, llm_settings

        return (
            classification_settings.chunk_classification_llm
            or llm_settings.classification_llm
            or llm_settings.general_llm
        )
    except Exception:
        return None


class ChunkTypeClassificationWorkflow:
    """Post-processing step that reassigns ChunkType for GENERAL/UNKNOWN chunks.

    Runs AFTER the deterministic chunking pipeline and BEFORE chunks are
    persisted. Controlled by CHUNK_TYPE_CLASSIFICATION_ENABLED in .env.

    Chunks reclassified here get chunk_type_source="llm"; all others keep
    chunk_type_source="deterministic" (the DocumentChunk default).
    """

    def __init__(
        self,
        *,
        llm_classifier: ChunkTypeLLMClassifier,
        enable_chunk_type_classification: bool | None = None,
    ) -> None:
        self.llm_classifier = llm_classifier
        self.enable_chunk_type_classification = (
            enable_chunk_type_classification
            if enable_chunk_type_classification is not None
            else _default_chunk_type_classification_enabled()
        )

    def classify_unresolved_chunks(
        self,
        chunks: list[DocumentChunk],
        *,
        progress_callback: Callable[[str], None] | None = None,
    ) -> int:
        """Reclassify GENERAL/UNKNOWN chunks in-place. Returns count reclassified."""
        if not self.enable_chunk_type_classification:
            self._emit(
                progress_callback,
                "Chunk-type classification disabled; skipping LLM reclassification.",
            )
            return 0

        if not self.llm_classifier.is_available():
            self._emit(
                progress_callback,
                "Chunk-type classification enabled but LLM classifier not available; skipping.",
            )
            return 0

        candidates = [c for c in chunks if c.chunk_type in _UNRESOLVED_TYPES]
        if not candidates:
            self._emit(progress_callback, "No GENERAL/UNKNOWN chunks to reclassify.")
            return 0

        self._emit(
            progress_callback,
            f"Reclassifying {len(candidates)} GENERAL/UNKNOWN chunk(s) via LLM...",
        )
        reclassified = 0
        for chunk in candidates:
            result = self.llm_classifier.classify(
                content=chunk.content,
                section_path=chunk.section_path,
            )
            if result is not None:
                chunk.chunk_type = result
                chunk.chunk_type_source = _CHUNK_TYPE_CLASSIFICATION_SOURCE
                reclassified += 1

        self._emit(
            progress_callback,
            f"LLM reclassified {reclassified}/{len(candidates)} chunk(s).",
        )
        return reclassified

    @staticmethod
    def _emit(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)
