from __future__ import annotations

from collections.abc import Callable

from src.application.workflows.classification import DocumentClassificationWorkflow
from src.application.workflows.ingestion.stages.classification_stage_result import (
    ClassificationStageResult,
)
from src.shared.activity import ActivityContext


class ClassificationStageRunner:
    def __init__(
        self,
        *,
        document_classification_workflow: DocumentClassificationWorkflow,
        commit: Callable[[], None],
    ) -> None:
        self.document_classification_workflow = document_classification_workflow
        self.commit = commit

    def run(
        self,
        *,
        document_graph,
        activity_context: ActivityContext | None = None,
    ) -> ClassificationStageResult:
        classification = self.document_classification_workflow.classify_document(
            document_graph,
            activity_context=activity_context,
        )
        self.commit()
        processing_metadata = (
            classification.result.processing_metadata
            if classification.result is not None
            else None
        )
        return ClassificationStageResult(
            classification=classification,
            classification_model=(
                processing_metadata.model_name if processing_metadata is not None else None
            ),
        )
