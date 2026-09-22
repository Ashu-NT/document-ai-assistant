import json

from src.application.evaluation.golden.aggregate_cross_reference_metrics import (
    AggregateCrossReferenceTypeMetrics,
)
from src.application.evaluation.golden.corpus_coverage_summary import (
    CorpusCoverageSummary,
)
from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationOutcome,
    GoldenDocumentEvaluationStatus,
)
from src.application.evaluation.golden.golden_evaluation_report import (
    GoldenEvaluationReport,
)
from src.application.evaluation.ingestion.models.cross_reference_evaluation_result import (
    CrossReferenceEvaluationResult,
    CrossReferenceTypeMetrics,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_result import (
    IngestionAssertionResult,
    IngestionExpectationCaseResult,
)
from src.application.evaluation.reproducibility import build_evaluation_run_metadata
from src.application.reporting.golden_evaluation import (
    GoldenEvaluationReportJsonSerializer,
    GoldenEvaluationReportMarkdownRenderer,
    GoldenEvaluationReportWriter,
)


def _sample_report() -> GoldenEvaluationReport:
    passing_structural = IngestionExpectationCaseResult(
        case_id="struct_doc_a",
        assertions=[
            IngestionAssertionResult(name="section_count", expected=5, actual=5, passed=True),
            IngestionAssertionResult(name="no_empty_chunks", expected=0, actual=0, passed=True),
        ],
    )
    failing_structural = IngestionExpectationCaseResult(
        case_id="struct_doc_b",
        assertions=[
            IngestionAssertionResult(name="section_count", expected=5, actual=3, passed=False),
            IngestionAssertionResult(
                name="chunk_hard_token_budget", expected="<= 310", actual="1 chunk(s) over budget", passed=False
            ),
        ],
    )
    cross_reference_result = CrossReferenceEvaluationResult(
        case_id="struct_doc_a",
        type_metrics=[
            CrossReferenceTypeMetrics(
                reference_type="section_reference",
                exhaustive=False,
                true_positives=2,
                false_negatives=1,
                false_positives=None,
                matched_clues=("clue a", "clue b"),
                missed_clues=("clue c",),
            )
        ],
        reconciliation_outcome_counts={"single_source": 3, "confirmed": 1},
        external_reference_clues_correctly_unresolved=1,
        external_reference_clues_incorrectly_resolved=0,
    )

    outcomes = [
        GoldenDocumentEvaluationOutcome(
            alias="doc_a",
            status=GoldenDocumentEvaluationStatus.EVALUATED,
            structural_result=passing_structural,
            cross_reference_result=cross_reference_result,
        ),
        GoldenDocumentEvaluationOutcome(
            alias="doc_b",
            status=GoldenDocumentEvaluationStatus.EVALUATED,
            structural_result=failing_structural,
            cross_reference_result=CrossReferenceEvaluationResult(case_id="struct_doc_b"),
        ),
        GoldenDocumentEvaluationOutcome(
            alias="doc_c",
            status=GoldenDocumentEvaluationStatus.CORPUS_MISSING,
            detail="expected file not found",
        ),
    ]

    return GoldenEvaluationReport(
        run_metadata=build_evaluation_run_metadata(
            parser_name="docling", parser_version="2.111.0", conversion_fingerprint="fp-1"
        ),
        corpus_coverage=CorpusCoverageSummary(
            expected=3, available=2, evaluated=2, missing_aliases=("doc_c",)
        ),
        document_outcomes=outcomes,
    )


class TestJsonSerialization:
    def test_serializes_to_valid_json_with_expected_structure(self) -> None:
        report = _sample_report()
        serializer = GoldenEvaluationReportJsonSerializer()

        payload = serializer.serialize(report)
        # Must be genuinely JSON-serializable, not just a dict of Python objects.
        round_tripped = json.loads(json.dumps(payload))

        assert round_tripped["corpus_coverage"]["expected"] == 3
        assert round_tripped["corpus_coverage"]["evaluated"] == 2
        assert round_tripped["summary"]["structural_passed_count"] == 1
        assert round_tripped["summary"]["structural_failed_count"] == 1
        assert round_tripped["summary"]["documents_not_evaluated"] == ["doc_c"]
        assert len(round_tripped["documents"]) == 3

        doc_a = next(d for d in round_tripped["documents"] if d["alias"] == "doc_a")
        assert doc_a["structural"]["passed"] is True
        assert doc_a["cross_references"]["type_metrics"][0]["reference_type"] == "section_reference"
        assert doc_a["cross_references"]["type_metrics"][0]["true_positives"] == 2
        assert doc_a["cross_references"]["reconciliation_outcome_counts"] == {
            "single_source": 3,
            "confirmed": 1,
        }

    def test_aggregate_cross_reference_metrics_included(self) -> None:
        report = _sample_report()
        payload = GoldenEvaluationReportJsonSerializer().serialize(report)

        aggregate = payload["cross_reference_type_metrics"]
        assert len(aggregate) == 1
        assert aggregate[0]["reference_type"] == "section_reference"
        assert aggregate[0]["true_positives"] == 2
        assert aggregate[0]["recall"] == 2 / 3


class TestMarkdownRendering:
    def test_render_includes_all_required_sections(self) -> None:
        report = _sample_report()
        rendered = GoldenEvaluationReportMarkdownRenderer().render(report)

        for heading in (
            "## Corpus",
            "## Structural",
            "## Chunking",
            "## Cross References",
            "## Reconciliation outcomes",
            "## Documents Not Evaluated",
            "## Reproducibility",
        ):
            assert heading in rendered

        assert "expected documents: `3`" in rendered
        assert "passed documents: `1`" in rendered
        assert "failed documents: `1`" in rendered
        assert "section_reference" in rendered
        assert "doc_c" in rendered  # listed as not-evaluated
        assert "docling 2.111.0" in rendered

    def test_render_does_not_collapse_into_a_single_score(self) -> None:
        rendered = GoldenEvaluationReportMarkdownRenderer().render(_sample_report())

        # Structural and cross-reference results must remain visibly
        # separate sections, never merged into one overall number.
        structural_index = rendered.index("## Structural")
        cross_reference_index = rendered.index("## Cross References")
        assert structural_index < cross_reference_index


class TestWriter:
    def test_write_json_and_markdown_to_disk(self, tmp_path) -> None:
        report = _sample_report()
        writer = GoldenEvaluationReportWriter()

        json_path = writer.write_json(report, tmp_path / "nested" / "report.json")
        markdown_path = writer.write_markdown(report, tmp_path / "nested" / "report.md")

        assert json_path.exists()
        assert markdown_path.exists()
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert payload["corpus_coverage"]["expected"] == 3
        assert "## Corpus" in markdown_path.read_text(encoding="utf-8")
