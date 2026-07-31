from __future__ import annotations

from collections.abc import Callable

from src.application.workflows.classification import DocumentClassificationWorkflow
from src.application.workflows.ingestion.stages.classification_stage_result import (
    ClassificationStageResult,
)
from src.shared.activity import ActivityContext
from src.shared.progress.progress_emitter import emit_progress


class ClassificationStageRunner:
    def __init__(
        self,
        *,
        document_classification_workflow: DocumentClassificationWorkflow,
        classification_enabled: bool,
        commit: Callable[[], None],
    ) -> None:
        self.document_classification_workflow = document_classification_workflow
        self.classification_enabled = classification_enabled
        self.commit = commit

    def run(
        self,
        *,
        document_graph,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> ClassificationStageResult:
        if not self.classification_enabled:
            emit_progress(progress_callback, self._skip_message())
            return ClassificationStageResult(
                classification=None,
                classification_model=None,
            )
        classification = self.document_classification_workflow.classify_document(
            document_graph,
            activity_context=activity_context,
        )
        self.commit()
        processing_metadata = (
            classification.result.processing_metadata
            if classification is not None and classification.result is not None
            else None
        )
        return ClassificationStageResult(
            classification=classification,
            classification_model=(
                processing_metadata.model_name if processing_metadata is not None else None
            ),
        )

    def _skip_message(self) -> str:
        return "Classification skipped by config."
