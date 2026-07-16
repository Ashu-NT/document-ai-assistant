from typing import Callable

from src.application.services.classification import ClassificationService
from src.application.workflows.classification.chunk_type_classification_workflow import (
    ChunkTypeClassificationWorkflow,
)
from src.domain.document import DocumentChunk


class FinalChunkClassificationRunner:
    """Resolves any still-unknown chunk types (when a chunk-type classifier
    is configured) on the final chunk set after chunk finalization."""

    def __init__(
        self,
        *,
        classification_service: ClassificationService,
        chunk_type_classification_workflow: ChunkTypeClassificationWorkflow | None = None,
    ) -> None:
        self.classification_service = classification_service
        self.chunk_type_classification_workflow = chunk_type_classification_workflow

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
