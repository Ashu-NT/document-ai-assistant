from __future__ import annotations

from collections.abc import Callable

from src.application.workflows.embedding import EmbeddedChunk, EmbeddingWorkflow
from src.application.workflows.ingestion.stages.vector_index_stage_result import (
    VectorIndexStageResult,
)
from src.shared.activity import ActivityContext


class VectorIndexStageRunner:
    def __init__(
        self,
        *,
        embedding_workflow: EmbeddingWorkflow,
        commit: Callable[[], None],
    ) -> None:
        self.embedding_workflow = embedding_workflow
        self.commit = commit

    def embed(
        self,
        *,
        final_graph,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> VectorIndexStageResult:
        embedded_chunks = self.embedding_workflow.embed_chunks(
            list(final_graph.chunks.values()),
            activity_context=activity_context,
            progress_callback=progress_callback,
        )
        return VectorIndexStageResult(
            embedded_chunks=embedded_chunks,
            embedding_model=self.embedding_workflow.embedding_service.model_name,
        )

    def index(
        self,
        *,
        document_id: str,
        embedded_chunks: list[EmbeddedChunk],
        replace_existing: bool,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        if replace_existing:
            self.embedding_workflow.delete_document_vectors(document_id)
        self.embedding_workflow.store_embedded_chunks(
            embedded_chunks,
            progress_callback=progress_callback,
        )
        self.commit()
