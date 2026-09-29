import json

from src.application.evaluation.golden.corpus_coverage_summary import CorpusCoverageSummary
from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationOutcome,
    GoldenDocumentEvaluationStatus,
)
from src.application.evaluation.golden.golden_evaluation_report import GoldenEvaluationReport
from src.application.evaluation.ingestion.models.ingestion_expectation_result import (
    IngestionAssertionResult,
    IngestionExpectationCaseResult,
)
from src.application.evaluation.ingestion.models.structural_baseline_provenance import (
    StructuralBaselineProvenance,
)
from src.application.evaluation.reproducibility import build_evaluation_run_metadata
from src.application.reporting.golden_evaluation import (
    GoldenEvaluationReportJsonSerializer,
    GoldenEvaluationReportMarkdownRenderer,
)


def _report_with_provenance(
    *, provenance: StructuralBaselineProvenance | None
) -> GoldenEvaluationReport:
    structural_result = IngestionExpectationCaseResult(
        case_id="struct_doc_a",
        assertions=[
            IngestionAssertionResult(name="section_count", expected=5, actual=5, passed=True),
        ],
        provenance=provenance,
    )
    outcome = GoldenDocumentEvaluationOutcome(
        alias="doc_a",
        status=GoldenDocumentEvaluationStatus.EVALUATED,
        structural_result=structural_result,
    )
    return GoldenEvaluationReport(
        run_metadata=build_evaluation_run_metadata(
            parser_name="docling",
            parser_version="2.126.0",
            conversion_fingerprint="fp-current",
        ),
        corpus_coverage=CorpusCoverageSummary(expected=1, available=1, evaluated=1),
        document_outcomes=[outcome],
    )


class TestNoProvenanceRecorded:
    def test_json_reports_none_not_a_fabricated_value(self) -> None:
        report = _report_with_provenance(provenance=None)
        payload = GoldenEvaluationReportJsonSerializer().serialize(report)

        doc_a = next(d for d in payload["documents"] if d["alias"] == "doc_a")
        assert doc_a["structural"]["baseline_provenance"] is None

    def test_markdown_omits_the_provenance_section_entirely(self) -> None:
        rendered = GoldenEvaluationReportMarkdownRenderer().render(
            _report_with_provenance(provenance=None)
        )

        assert "Baseline provenance" not in rendered

    def test_empty_provenance_object_is_also_treated_as_not_recorded(self) -> None:
        # An explicitly-constructed-but-empty StructuralBaselineProvenance
        # (all fields None) must render identically to "not recorded", per
        # `is_recorded` - never surfaced as if something were known.
        report = _report_with_provenance(provenance=StructuralBaselineProvenance())
        payload = GoldenEvaluationReportJsonSerializer().serialize(report)
        rendered = GoldenEvaluationReportMarkdownRenderer().render(report)

        doc_a = next(d for d in payload["documents"] if d["alias"] == "doc_a")
        assert doc_a["structural"]["baseline_provenance"] is None
        assert "Baseline provenance" not in rendered


class TestProvenanceMatchesCurrentRun:
    def test_json_includes_the_recorded_fields_verbatim(self) -> None:
        provenance = StructuralBaselineProvenance(
            parser_name="docling",
            parser_version="2.126.0",
            conversion_fingerprint="fp-current",
        )
        report = _report_with_provenance(provenance=provenance)

        payload = GoldenEvaluationReportJsonSerializer().serialize(report)
        round_tripped = json.loads(json.dumps(payload))

        doc_a = next(d for d in round_tripped["documents"] if d["alias"] == "doc_a")
        assert doc_a["structural"]["baseline_provenance"] == {
            "parser_name": "docling",
            "parser_version": "2.126.0",
            "conversion_fingerprint": "fp-current",
        }

    def test_markdown_reports_a_match_diagnostically(self) -> None:
        provenance = StructuralBaselineProvenance(
            parser_name="docling",
            parser_version="2.126.0",
            conversion_fingerprint="fp-current",
        )
        rendered = GoldenEvaluationReportMarkdownRenderer().render(
            _report_with_provenance(provenance=provenance)
        )

        assert "### Baseline provenance (diagnostic only)" in rendered
        assert "matches current run" in rendered


class TestProvenanceDiffersFromCurrentRun:
    def test_markdown_reports_a_difference_diagnostically_never_as_a_failure(self) -> None:
        provenance = StructuralBaselineProvenance(
            parser_name="docling",
            parser_version="2.111.0",
            conversion_fingerprint="fp-old",
        )
        report = _report_with_provenance(provenance=provenance)

        rendered = GoldenEvaluationReportMarkdownRenderer().render(report)

        assert "differs from current run" in rendered
        # A provenance mismatch must never turn structural pass/fail
        # reporting into a failure by itself.
        assert report.structural_passed_count == 1
        assert report.structural_failed_count == 0
