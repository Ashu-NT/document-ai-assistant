import copy
from typing import cast

from src.application.workflows.ingestion.stages.classification_stage_runner import (
    ClassificationStageRunner,
)
from src.domain.classification import DocumentClassification


class FakeDocumentClassificationWorkflow:
    def __init__(self, classification) -> None:
        self.classification = classification
        self.calls = []

    def classify_document(self, document_graph, activity_context=None):
        self.calls.append(document_graph)
        classification = copy.deepcopy(self.classification)
        classification.document_id = document_graph.document.document_id
        return classification


def _make_runner(
    *,
    classification_enabled: bool,
    document_classification_workflow=None,
    commit_calls: list[str] | None = None,
):
    calls = commit_calls if commit_calls is not None else []
    runner = ClassificationStageRunner(
        document_classification_workflow=(
            document_classification_workflow
            or FakeDocumentClassificationWorkflow(None)
        ),
        classification_enabled=classification_enabled,
        commit=lambda: calls.append("commit"),
    )
    return runner, calls


def test_classification_stage_runner_calls_workflow_when_enabled(
    sample_document_graph,
    sample_document_classification,
) -> None:
    fake_workflow = FakeDocumentClassificationWorkflow(sample_document_classification)
    commit_calls: list[str] = []
    runner, commit_calls = _make_runner(
        classification_enabled=True,
        document_classification_workflow=fake_workflow,
        commit_calls=commit_calls,
    )

    result = runner.run(document_graph=sample_document_graph)

    assert fake_workflow.calls == [sample_document_graph]
    assert commit_calls == ["commit"]
    assert result.classification is not None
    classification = cast(DocumentClassification, result.classification)
    assert classification.document_id == sample_document_graph.document.document_id


def test_classification_stage_runner_skips_workflow_when_disabled(
    sample_document_graph,
    sample_document_classification,
) -> None:
    fake_workflow = FakeDocumentClassificationWorkflow(sample_document_classification)
    commit_calls: list[str] = []
    runner, commit_calls = _make_runner(
        classification_enabled=False,
        document_classification_workflow=fake_workflow,
        commit_calls=commit_calls,
    )
    progress_messages: list[str] = []

    result = runner.run(
        document_graph=sample_document_graph,
        progress_callback=progress_messages.append,
    )

    assert fake_workflow.calls == []
    assert commit_calls == []
    assert result.classification is None
    assert result.classification_model is None
    assert progress_messages == ["Classification skipped by config."]
