from src.application.evaluation import (
    RetrievalBenchmarkCase,
    RetrievalBenchmarkCaseResult,
    RetrievalBenchmarkReport,
)
from src.application.reporting.retrieval_benchmark import (
    RetrievalBenchmarkReportMarkdownRenderer,
)
from src.application.workflows.retrieval.retrieval_query_intent import RetrievalQueryIntent
from src.domain.retrieval import RetrievalQuery

from tests.unit.application.reporting.retrieval_benchmark.report_builders import (
    build_sample_report,
)


def test_markdown_renderer_includes_breakdowns_and_failure_debug_details() -> None:
    report = build_sample_report()
    renderer = RetrievalBenchmarkReportMarkdownRenderer()

    markdown = renderer.render(report)

    assert "# Retrieval Benchmark Report" in markdown
    assert "## Breakdown by Document Family" in markdown
    assert "## Breakdown by Query Type" in markdown
    assert "| manual | 1 | 1.000 |" in markdown
    assert "| procedure_lookup | 1 | 1.000 |" in markdown
    assert "## Failure Diagnostics" in markdown
    assert "### `D-001` What pressure range is supported?" in markdown
    assert "- expected document: `datasheet_mk311xxx`" in markdown
    assert "- expected file: `datasheet.pdf`" in markdown
    assert "- expected section path: `Pressure Range`" in markdown
    assert "- expected page: `2`" in markdown
    assert "Context expansion recovered the expected evidence after the anchor miss." in markdown
    assert "| 1 | chunk_datasheet_intro | doc_datasheet | dense | 0.790 | 1 | General Notes |" in markdown
    assert "| 2 | chunk_datasheet_pressure | doc_datasheet | context | 0.630 | 2 | Pressure Range |" in markdown


def test_markdown_renderer_reports_no_expected_intent_when_none_of_the_cases_set_it() -> None:
    report = build_sample_report()
    renderer = RetrievalBenchmarkReportMarkdownRenderer()

    markdown = renderer.render(report)

    assert "## Intent Classification" in markdown
    assert "- no benchmark cases set `expected_intent`" in markdown


def test_markdown_renderer_includes_accuracy_and_confusion_matrix_when_intent_expected() -> None:
    case_hit = RetrievalBenchmarkCase(
        case_id="c1",
        query=RetrievalQuery(query_id="c1", query_text="What is the safety warning?"),
        expected_intent=RetrievalQueryIntent.SAFETY,
    )
    case_miss = RetrievalBenchmarkCase(
        case_id="c2",
        query=RetrievalQuery(query_id="c2", query_text="What is the maintenance procedure?"),
        expected_intent=RetrievalQueryIntent.PROCEDURE,
    )
    report = RetrievalBenchmarkReport(
        case_results=[
            RetrievalBenchmarkCaseResult(
                case=case_hit,
                actual_intent=RetrievalQueryIntent.SAFETY,
            ),
            RetrievalBenchmarkCaseResult(
                case=case_miss,
                actual_intent=RetrievalQueryIntent.MAINTENANCE,
            ),
        ]
    )
    renderer = RetrievalBenchmarkReportMarkdownRenderer()

    markdown = renderer.render(report)

    assert "## Intent Classification" in markdown
    assert "- accuracy: `0.500`" in markdown
    assert "| safety | safety | 1 |" in markdown
    assert "| procedure | maintenance | 1 |" in markdown
