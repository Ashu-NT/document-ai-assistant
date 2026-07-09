from unittest.mock import MagicMock

from src.application.reporting.document_parsing.parsing import OcrTraceSerializer


def test_serialize_returns_none_for_none_trace() -> None:
    assert OcrTraceSerializer().serialize(None) is None


def test_serialize_returns_none_for_mock_trace() -> None:
    assert OcrTraceSerializer().serialize(MagicMock()) is None


def test_serialize_returns_none_when_shape_is_incomplete() -> None:
    trace = MagicMock()
    trace.analyzed_pages = "not-a-list"
    assert OcrTraceSerializer().serialize(trace) is None


def test_serialize_builds_expected_payload() -> None:
    trace = type(
        "FakeOcrTrace",
        (),
        {
            "analyzed_pages": [
                type("PageAnalysis", (), {"page_number": 1, "is_text_poor": True})(),
                type("PageAnalysis", (), {"page_number": 2, "is_text_poor": False})(),
            ],
            "selected_targets": [object()],
            "execution_results": [object(), object()],
            "warnings": ["low confidence"],
            "added_synthetic_elements": 3,
            "updated_asset_elements": 1,
            "trace_path": "/tmp/trace.json",
        },
    )()

    payload = OcrTraceSerializer().serialize(trace)

    assert payload == {
        "text_poor_pages": [1],
        "selected_target_count": 1,
        "execution_count": 2,
        "added_synthetic_elements": 3,
        "updated_asset_elements": 1,
        "warnings": ["low confidence"],
        "trace_path": "/tmp/trace.json",
    }
