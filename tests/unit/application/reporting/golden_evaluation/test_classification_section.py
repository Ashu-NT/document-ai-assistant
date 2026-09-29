import json

from src.application.evaluation.classification.classification_attempt import (
    ClassificationAttempt,
    ClassificationValidationOutcome,
)
from src.application.evaluation.classification.classification_expectation_case import (
    ClassificationExpectationCase,
)
from src.application.evaluation.classification.classification_review_status import (
    ClassificationReviewStatus,
)
from src.application.evaluation.classification.golden_classification_document_result import (
    ClassificationStageStatus,
    GoldenClassificationDocumentResult,
)
from src.application.evaluation.golden.corpus_coverage_summary import CorpusCoverageSummary
from src.application.evaluation.golden.golden_evaluation_report import GoldenEvaluationReport
from src.application.evaluation.reproducibility import build_evaluation_run_metadata
from src.application.reporting.golden_evaluation import (
    GoldenEvaluationReportJsonSerializer,
    GoldenEvaluationReportMarkdownRenderer,
)
from src.domain.common import DocumentType


def _attempt(*, predicted: DocumentType, confidence: float, passed_gate: bool) -> ClassificationAttempt:
    return ClassificationAttempt(
        predicted_document_type=predicted,
        predicted_label=predicted.value,
        confidence=confidence,
        rationale="because",
        processing_metadata=None,
        confidence_threshold=0.6,
        passed_confidence_gate=passed_gate,
        validation_outcome=(
            ClassificationValidationOutcome.VALID
            if passed_gate
            else ClassificationValidationOutcome.NOT_APPLICABLE
        ),
        model_name="qwen3:8b",
    )


def _report_with_classification() -> GoldenEvaluationReport:
    results = [
        GoldenClassificationDocumentResult(
            alias="doc_reviewed_correct",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=ClassificationExpectationCase(
                document_alias="doc_reviewed_correct",
                expected_document_type=DocumentType.MANUAL,
                review_status=ClassificationReviewStatus.REVIEWED,
            ),
            attempt=_attempt(predicted=DocumentType.MANUAL, confidence=0.95, passed_gate=True),
        ),
        GoldenClassificationDocumentResult(
            alias="doc_candidate_only",
            stage_status=ClassificationStageStatus.EVALUATED,
            expectation=ClassificationExpectationCase(
                document_alias="doc_candidate_only",
                expected_document_type=DocumentType.DATASHEET,
                review_status=ClassificationReviewStatus.CANDIDATE,
            ),
            attempt=_attempt(predicted=DocumentType.DATASHEET, confidence=0.8, passed_gate=True),
        ),
        GoldenClassificationDocumentResult(
            alias="doc_failed",
            stage_status=ClassificationStageStatus.EXECUTION_FAILED,
            execution_error="RuntimeError: llm down",
        ),
    ]
    return GoldenEvaluationReport(
        run_metadata=build_evaluation_run_metadata(
            parser_name="docling",
            parser_version="2.111.0",
            classification_model="qwen3:8b",
            classification_execution_mode="fresh_model",
            classification_confidence_threshold=0.6,
            classification_allow_reclassification=False,
            classification_use_cache=False,
            classification_prompt_version="v1",
        ),
        corpus_coverage=CorpusCoverageSummary(expected=3, available=3, evaluated=3),
        document_outcomes=[],
        classification_results=results,
    )


class TestJsonSerialization:
    def test_classification_section_is_present_and_json_serializable(self) -> None:
        report = _report_with_classification()
        payload = GoldenEvaluationReportJsonSerializer().serialize(report)
        round_tripped = json.loads(json.dumps(payload))

        classification = round_tripped["classification"]
        assert classification["metrics"]["executed_count"] == 2
        assert classification["metrics"]["execution_failed_count"] == 1
        # Only the REVIEWED, non-ambiguous document is in the accuracy
        # denominator.
        assert classification["metrics"]["reviewed_eligible_document_count"] == 1
        assert classification["metrics"]["raw_accuracy"] == 1.0
        assert classification["metrics"]["confusion_matrix"] == {"manual": {"manual": 1}}

        docs_by_alias = {d["alias"]: d for d in classification["documents"]}
        assert docs_by_alias["doc_candidate_only"]["eligible_for_accuracy"] is False
        assert docs_by_alias["doc_failed"]["attempt"] is None
        assert "llm down" in docs_by_alias["doc_failed"]["execution_error"]

    def test_empty_classification_results_still_serializes(self) -> None:
        report = GoldenEvaluationReport(
            run_metadata=build_evaluation_run_metadata(),
            corpus_coverage=CorpusCoverageSummary(expected=0, available=0, evaluated=0),
            document_outcomes=[],
        )
        payload = GoldenEvaluationReportJsonSerializer().serialize(report)
        round_tripped = json.loads(json.dumps(payload))

        assert round_tripped["classification"]["documents"] == []
        assert round_tripped["classification"]["metrics"]["reviewed_eligible_document_count"] == 0


class TestMarkdownRendering:
    def test_classification_section_present_with_confusion_matrix_and_per_document_table(
        self,
    ) -> None:
        rendered = GoldenEvaluationReportMarkdownRenderer().render(_report_with_classification())

        assert "## Classification" in rendered
        assert "### Confusion matrix" in rendered
        assert "### Per-document results" in rendered
        assert "doc_reviewed_correct" in rendered
        assert "doc_candidate_only" in rendered
        assert "doc_failed" in rendered
        assert "fresh_model" in rendered  # reproducibility section

    def test_zero_reviewed_labels_states_this_explicitly_rather_than_fabricating_accuracy(
        self,
    ) -> None:
        report = GoldenEvaluationReport(
            run_metadata=build_evaluation_run_metadata(),
            corpus_coverage=CorpusCoverageSummary(expected=1, available=1, evaluated=1),
            document_outcomes=[],
            classification_results=[
                GoldenClassificationDocumentResult(
                    alias="doc_candidate_only",
                    stage_status=ClassificationStageStatus.EVALUATED,
                    expectation=ClassificationExpectationCase(
                        document_alias="doc_candidate_only",
                        expected_document_type=DocumentType.MANUAL,
                        review_status=ClassificationReviewStatus.CANDIDATE,
                    ),
                    attempt=_attempt(predicted=DocumentType.MANUAL, confidence=0.9, passed_gate=True),
                ),
            ],
        )

        rendered = GoldenEvaluationReportMarkdownRenderer().render(report)

        assert "No golden classification label has been human-reviewed yet" in rendered

    def test_no_classification_results_renders_explicit_not_evaluated_message(self) -> None:
        report = GoldenEvaluationReport(
            run_metadata=build_evaluation_run_metadata(),
            corpus_coverage=CorpusCoverageSummary(expected=0, available=0, evaluated=0),
            document_outcomes=[],
        )

        rendered = GoldenEvaluationReportMarkdownRenderer().render(report)

        assert "## Classification" in rendered
        assert "Classification was not evaluated in this run" in rendered
