from __future__ import annotations

from collections.abc import Callable

from src.application.workflows.classification import (
    PostClassificationChunkFinalizationWorkflow,
)
from src.application.workflows.ingestion.stages.finalization_stage_result import (
    FinalizationStageResult,
)
from src.shared.activity import ActivityContext


class FinalizationStageRunner:
    def __init__(
        self,
        *,
        post_classification_chunk_finalization_workflow: (
            PostClassificationChunkFinalizationWorkflow
        ),
        question_generation_model_loader: Callable[[], str | None],
        commit: Callable[[], None],
    ) -> None:
        self.post_classification_chunk_finalization_workflow = (
            post_classification_chunk_finalization_workflow
        )
        self.question_generation_model_loader = question_generation_model_loader
        self.commit = commit

    def run(
        self,
        *,
        document_id: str,
        enable_question_generation: bool | None,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> FinalizationStageResult:
        final_graph = self.post_classification_chunk_finalization_workflow.finalize(
            document_id,
            activity_context=activity_context,
            progress_callback=progress_callback,
            embed_final_chunks=False,
            enable_question_generation=enable_question_generation,
        )
        self.commit()
        return FinalizationStageResult(
            final_graph=final_graph,
            question_generation_model=self.question_generation_model_loader(),
        )
