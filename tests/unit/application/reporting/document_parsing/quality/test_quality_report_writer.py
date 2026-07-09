import json
from unittest.mock import MagicMock

from src.application.reporting.document_parsing.quality import QualityReportWriter


def _make_quality_result(*, passed: bool = True) -> MagicMock:
    result = MagicMock()
    result.passed = passed
    result.summary.return_value = "PASS 3/3 checks passed (0 errors, 0 warnings)"
    result.checks = []
    return result


def test_write_creates_json_file(tmp_path) -> None:
    writer = QualityReportWriter(output_dir=tmp_path)
    path = writer.write(
        "doc1",
        parse_result=_make_quality_result(),
        chunk_result=_make_quality_result(),
    )

    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "parsing" in data
    assert "chunking" in data
    assert "overall_passed" in data


def test_write_filename_contains_document_id(tmp_path) -> None:
    writer = QualityReportWriter(output_dir=tmp_path)
    path = writer.write(
        "docXYZ",
        parse_result=_make_quality_result(),
        chunk_result=_make_quality_result(),
    )

    assert "docXYZ" in path.name


def test_write_runs_no_quality_checks_itself() -> None:
    """QualityReportWriter only serializes already-computed results -- it
    must not import or invoke DocumentQualityGate itself (that orchestration
    moved to ParsingWorkflow)."""
    import src.application.reporting.document_parsing.quality.quality_report_writer as module

    assert "DocumentQualityGate" not in dir(module)
