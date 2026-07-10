from typing import Callable

from src.application.services.classification import ClassificationService
from src.application.workflows.classification.chunk_classification_workflow import (
    ChunkClassificationWorkflow,
)
from src.application.workflows.classification.chunk_type_classification_workflow import (
    ChunkTypeClassificationWorkflow,
)
from src.application.workflows.common import run_bounded_concurrent_map
from src.domain.classification import ChunkClassification
from src.domain.document import DocumentChunk
from src.shared.activity import ActivityContext
from src.shared.exceptions import ApplicationError
from src.shared.progress import emit_progress

_MAX_CONCURRENT_CHUNK_CLASSIFICATIONS = 8


class FinalChunkClassificationRunner:
    """Classifies the final chunk set after chunk finalization: resolves any
    still-unknown chunk types (when a chunk-type classifier is configured)
    and, when chunk classification is enabled, classifies every final chunk
    concurrently via the shared `run_bounded_concurrent_map` before
    persisting the results in a single sequential (thread-unsafe) write."""

    def __init__(
        self,
        *,
        classification_service: ClassificationService,
        chunk_classification_workflow: ChunkClassificationWorkflow | None = None,
        chunk_type_classification_workflow: ChunkTypeClassificationWorkflow | None = None,
        enable_chunk_classification: bool = False,
        max_concurrency: int = _MAX_CONCURRENT_CHUNK_CLASSIFICATIONS,
    ) -> None:
        self.classification_service = classification_service
        self.chunk_classification_workflow = chunk_classification_workflow
        self.chunk_type_classification_workflow = chunk_type_classification_workflow
        self.enable_chunk_classification = enable_chunk_classification
        self.max_concurrency = max_concurrency

    def classify_chunk_types_if_enabled(
        self,
        *,
        chunks: list[DocumentChunk],
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        if self.chunk_type_classification_workflow is None:
            return
        self.chunk_type_classification_workflow.classify_unresolved_chunks(
            chunks,
            progress_callback=progress_callback,
        )

    def classify_chunks_if_enabled(
        self,
        *,
        chunks: list[DocumentChunk],
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        if not self.enable_chunk_classification:
            emit_progress(
                progress_callback,
                "Chunk classification disabled; skipping final chunk classification.",
            )
            return

        chunk_classification_workflow = self.chunk_classification_workflow
        if chunk_classification_workflow is None:
            raise ApplicationError(
                "Chunk classification is enabled but no chunk classification workflow is configured.",
            )

        total_chunks = len(chunks)
        emit_progress(
            progress_callback,
            f"Classifying {total_chunks} final chunk(s)...",
        )

        # The LLM call + validation (classify_chunk_without_saving) has no
        # shared state and is safe to run concurrently; the DB write
        # (save_chunk_classification) is not safe across threads, so it
        # stays in a sequential pass afterward.
        classifications: list[ChunkClassification] = run_bounded_concurrent_map(
            chunks,
            lambda chunk: chunk_classification_workflow.classify_chunk_without_saving(
                chunk,
                activity_context=activity_context,
            ),
            max_concurrency=self.max_concurrency,
        )

        self.classification_service.save_chunk_classifications(
            classifications,
            activity_context=activity_context,
        )
        emit_progress(
            progress_callback,
            f"Classified {total_chunks} final chunk(s).",
        )
