from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable

from src.application.services.ai import LLMService
from src.application.workflows.parsing.builders.chunking.builders.chunk_type_llm_classifier import (
    ChunkTypeLLMClassifier,
)
from src.domain.common import ChunkType
from src.domain.document import DocumentChunk

_UNRESOLVED_TYPES = {ChunkType.GENERAL, ChunkType.UNKNOWN}
_CHUNK_TYPE_CLASSIFICATION_SOURCE = "llm"
_MAX_CONCURRENT_CHUNK_TYPE_CLASSIFICATIONS = 8


def _default_chunk_type_classification_enabled() -> bool:
    try:
        from src.config.settings import classification_settings

        return classification_settings.chunk_type_classification_enabled
    except Exception:
        return False


def _default_chunk_type_classification_model() -> str | None:
    try:
        from src.config.settings import classification_settings, llm_settings

        return (
            classification_settings.chunk_classification_llm
            or llm_settings.classification_llm
            or llm_settings.general_llm
        )
    except Exception:
        return None


def _default_chunk_type_classification_confidence_threshold() -> float:
    try:
        from src.config.settings import classification_settings

        return classification_settings.chunk_classification_confidence_threshold
    except Exception:
        return 0.70


@dataclass(slots=True)
class _ChunkTypeClassificationOutcome:
    chunk: DocumentChunk
    resolved_type: ChunkType | None = None
    error: str | None = None


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
        llm_service: LLMService,
        classification_model: str | None = None,
        enable_chunk_type_classification: bool | None = None,
        confidence_threshold: float | None = None,
    ) -> None:
        model = classification_model or _default_chunk_type_classification_model()
        self.llm_classifier = ChunkTypeLLMClassifier(
            llm_service=llm_service,
            model=model,
            confidence_threshold=(
                confidence_threshold
                if confidence_threshold is not None
                else _default_chunk_type_classification_confidence_threshold()
            ),
        )
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
        max_workers = min(len(candidates), _MAX_CONCURRENT_CHUNK_TYPE_CLASSIFICATIONS)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(
                executor.map(
                    self._classify_candidate,
                    candidates,
                )
            )

        reclassified = 0
        failures: list[_ChunkTypeClassificationOutcome] = []
        for outcome in results:
            if outcome.resolved_type is not None:
                outcome.chunk.chunk_type = outcome.resolved_type
                outcome.chunk.chunk_type_source = _CHUNK_TYPE_CLASSIFICATION_SOURCE
                reclassified += 1
                continue
            if outcome.error is not None:
                failures.append(outcome)

        if failures:
            self._emit(
                progress_callback,
                self._build_failure_message(failures),
            )

        self._emit(
            progress_callback,
            (
                f"LLM reclassified {reclassified}/{len(candidates)} chunk(s)"
                + (
                    f"; skipped {len(failures)} failed chunk(s)."
                    if failures
                    else "."
                )
            ),
        )
        return reclassified

    def _classify_candidate(
        self,
        chunk: DocumentChunk,
    ) -> _ChunkTypeClassificationOutcome:
        try:
            return _ChunkTypeClassificationOutcome(
                chunk=chunk,
                resolved_type=self.llm_classifier.classify(
                    content=chunk.content,
                    section_path=chunk.section_path,
                ),
            )
        except Exception as exc:
            return _ChunkTypeClassificationOutcome(
                chunk=chunk,
                error=f"{type(exc).__name__}: {exc}",
            )

    @staticmethod
    def _build_failure_message(
        failures: list[_ChunkTypeClassificationOutcome],
    ) -> str:
        preview = "; ".join(
            f"{failure.chunk.chunk_id} ({failure.error})"
            for failure in failures[:3]
        )
        suffix = " ..." if len(failures) > 3 else ""
        return (
            "Chunk-type reclassification skipped "
            f"{len(failures)} chunk(s) after LLM/schema failures. "
            f"First failures: {preview}{suffix}"
        )

    @staticmethod
    def _emit(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)
