import json

from src.application.evaluation import (
    RetrievalBenchmarkReportWriter,
)

from tests.unit.application.evaluation.retrieval.benchmarking.reporting.report_builders import (
    build_sample_report,
)


def test_report_writer_writes_json_and_markdown_outputs(tmp_path) -> None:
    report = build_sample_report()
    writer = RetrievalBenchmarkReportWriter()
    json_path = tmp_path / "reports" / "retrieval_report.json"
    markdown_path = tmp_path / "reports" / "retrieval_report.md"

    written_json_path = writer.write_json(report, json_path)
    written_markdown_path = writer.write_markdown(report, markdown_path)

    json_payload = json.loads(written_json_path.read_text(encoding="utf-8"))
    markdown = written_markdown_path.read_text(encoding="utf-8")

    assert written_json_path == json_path
    assert written_markdown_path == markdown_path
    assert json_payload["summary"]["case_count"] == 3
    assert "Retrieval Benchmark Report" in markdown
