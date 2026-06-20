from src.application.evaluation import (
    RetrievalBenchmarkReportMarkdownRenderer,
)

from tests.unit.application.evaluation.retrieval.benchmarking.reporting.report_builders import (
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
