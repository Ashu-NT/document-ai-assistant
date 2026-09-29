import json

from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)
from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
)
from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractionApplicabilityDeclaration,
    ExtractionExpectationCase,
)
from src.application.evaluation.extraction.extraction_applicability import (
    ExtractionApplicability,
)
from src.application.evaluation.extraction.golden_extraction_document_result import (
    ExtractionScopeRunOutcome,
    ExtractionStageStatus,
    GoldenExtractionDocumentResult,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchOutcome,
    ExtractionMatchResult,
)
from src.application.evaluation.golden.corpus_coverage_summary import (
    CorpusCoverageSummary,
)
from src.application.evaluation.golden.golden_evaluation_report import (
    GoldenEvaluationReport,
)
from src.application.evaluation.reproducibility import build_evaluation_run_metadata
from src.application.reporting.golden_evaluation.renderers.golden_evaluation_report_markdown_renderer import (
    GoldenEvaluationReportMarkdownRenderer,
)
from src.application.reporting.golden_evaluation.serializers.golden_evaluation_report_json_serializer import (
    GoldenEvaluationReportJsonSerializer,
)


def _empty_report(**extraction_metadata) -> GoldenEvaluationReport:
    return GoldenEvaluationReport(
        run_metadata=build_evaluation_run_metadata(**extraction_metadata),
        corpus_coverage=CorpusCoverageSummary(expected=1, available=1, evaluated=1),
    )


def _report_with_one_match() -> GoldenEvaluationReport:
    expectation = ExtractionExpectationCase(
        case_id="e1",
        document_alias="doc_a",
        entity_type=ExtractionEntityType.MANUFACTURER,
        scope=ExtractionEvaluationScope.whole_document(),
        completeness=ExtractionCompleteness.PRESENCE_ONLY,
        expected_fields={"name": "Acme"},
    )
    match = ExtractionMatchResult(
        outcome=ExtractionMatchOutcome.MATCHED,
        entity_type="manufacturer",
        group_completeness=ExtractionCompleteness.PRESENCE_ONLY,
        expectation=expectation,
        actual_entity_id="m1",
    )
    declaration = ExtractionApplicabilityDeclaration(
        declaration_id="d1",
        document_alias="doc_a",
        entity_type=ExtractionEntityType.MAINTENANCE_INTERVAL,
        scope=ExtractionEvaluationScope.whole_document(),
        applicability=ExtractionApplicability.NOT_APPLICABLE,
        reason="external publication",
    )
    document_result = GoldenExtractionDocumentResult(
        alias="doc_a",
        scope_outcomes=[
            ExtractionScopeRunOutcome(
                document_alias="doc_a",
                scope=ExtractionEvaluationScope.whole_document(),
                stage_status=ExtractionStageStatus.EVALUATED,
                match_results=[match],
                applicability_declarations=[declaration],
            )
        ],
    )
    return GoldenEvaluationReport(
        run_metadata=build_evaluation_run_metadata(
            extraction_model="qwen-test",
            extraction_execution_mode="fresh_model",
        ),
        corpus_coverage=CorpusCoverageSummary(expected=1, available=1, evaluated=1),
        extraction_results=[document_result],
    )


class TestExtractionSectionEmpty:
    def test_markdown_reports_not_evaluated_when_no_results(self) -> None:
        markdown = GoldenEvaluationReportMarkdownRenderer().render(_empty_report())
        assert "Extraction was not evaluated in this run" in markdown

    def test_json_extraction_section_present_and_empty(self) -> None:
        payload = GoldenEvaluationReportJsonSerializer().serialize(_empty_report())
        assert payload["extraction"]["documents"] == []
        assert payload["extraction"]["applicability_counts"] == {
            "applicable": 0,
            "not_applicable": 0,
            "not_assessed": 0,
        }

    def test_phase1_and_phase2a_sections_unaffected_by_empty_extraction(self) -> None:
        payload = GoldenEvaluationReportJsonSerializer().serialize(_empty_report())
        assert "classification" in payload
        assert "documents" in payload
        assert payload["summary"]["structural_passed_count"] == 0


class TestExtractionSectionWithResults:
    def test_json_and_markdown_agree_on_applicability_counts(self) -> None:
        report = _report_with_one_match()
        payload = GoldenEvaluationReportJsonSerializer().serialize(report)
        markdown = GoldenEvaluationReportMarkdownRenderer().render(report)

        assert payload["extraction"]["applicability_counts"]["not_applicable"] == 1
        assert "NOT_APPLICABLE: `1`" in markdown

    def test_candidate_metrics_are_not_authoritative_label_present(self) -> None:
        markdown = GoldenEvaluationReportMarkdownRenderer().render(_report_with_one_match())
        assert "NON-AUTHORITATIVE" in markdown
        assert "CANDIDATE (non-authoritative)" in markdown

    def test_reviewed_table_empty_when_nothing_reviewed(self) -> None:
        payload = GoldenEvaluationReportJsonSerializer().serialize(_report_with_one_match())
        assert payload["extraction"]["metrics_reviewed"] == []
        assert len(payload["extraction"]["metrics_candidate_non_authoritative"]) == 1

    def test_json_is_actually_json_serializable(self) -> None:
        payload = GoldenEvaluationReportJsonSerializer().serialize(_report_with_one_match())
        # Round-trips through the real json module - not just a plain dict.
        json.dumps(payload)

    def test_reproducibility_metadata_present_in_markdown(self) -> None:
        markdown = GoldenEvaluationReportMarkdownRenderer().render(_report_with_one_match())
        assert "extraction model: `qwen-test`" in markdown
        assert "extraction execution mode: `fresh_model`" in markdown


class TestNoReportClobbering:
    def test_extraction_results_default_empty_leaves_classification_untouched(self) -> None:
        """A report built the OLD way (no extraction_results kwarg at all)
        must still serialize/render without error - Phase 1/2A callers are
        never forced to know about Phase 2B."""
        report = GoldenEvaluationReport(
            run_metadata=build_evaluation_run_metadata(),
            corpus_coverage=CorpusCoverageSummary(expected=1, available=1, evaluated=1),
        )
        payload = GoldenEvaluationReportJsonSerializer().serialize(report)
        markdown = GoldenEvaluationReportMarkdownRenderer().render(report)
        assert payload["extraction"]["documents"] == []
        assert "## Classification" in markdown
        assert "## Extraction (Phase 2B)" in markdown
