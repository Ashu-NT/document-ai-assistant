from unittest.mock import MagicMock

from src.application.reporting.document_parsing.quality import (
    QualityResultSerializer,
)


def _make_quality_result(*, passed: bool, summary: str = "PASS") -> MagicMock:
    result = MagicMock()
    result.passed = passed
    result.summary.return_value = summary
    result.checks = [
        MagicMock(
            check_name="section_count",
            passed=passed,
            severity="warning",
            message="ok",
            details={},
        )
    ]
    return result


def test_serialize_includes_document_id_and_both_sections() -> None:
    serializer = QualityResultSerializer()
    payload = serializer.serialize(
        "doc1",
        parse_result=_make_quality_result(passed=True),
        chunk_result=_make_quality_result(passed=True),
    )

    assert payload["document_id"] == "doc1"
    assert "parsing" in payload
    assert "chunking" in payload


def test_serialize_overall_passed_true_only_when_both_pass() -> None:
    serializer = QualityResultSerializer()

    both_pass = serializer.serialize(
        "doc1",
        parse_result=_make_quality_result(passed=True),
        chunk_result=_make_quality_result(passed=True),
    )
    one_fails = serializer.serialize(
        "doc1",
        parse_result=_make_quality_result(passed=True),
        chunk_result=_make_quality_result(passed=False),
    )

    assert both_pass["overall_passed"] is True
    assert one_fails["overall_passed"] is False


def test_serialize_result_includes_check_details() -> None:
    serializer = QualityResultSerializer()
    payload = serializer.serialize(
        "doc1",
        parse_result=_make_quality_result(passed=True),
        chunk_result=_make_quality_result(passed=True),
    )

    checks = payload["parsing"]["checks"]
    assert checks[0]["name"] == "section_count"
    assert checks[0]["passed"] is True
