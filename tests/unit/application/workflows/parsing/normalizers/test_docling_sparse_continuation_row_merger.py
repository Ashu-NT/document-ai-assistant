from src.application.workflows.parsing.normalizers.docling_sparse_continuation_row_merger import (
    DoclingSparseContinuationRowMerger,
)
from src.domain.assets import TableCellSpan


def test_merge_attaches_sparse_continuation_row_to_previous_record() -> None:
    rows = [
        ["Cause", "Corrective action"],
        ["Blocked filter", "Replace the filter and"],
        ["", "clean the housing before restart."],
    ]

    merged = DoclingSparseContinuationRowMerger().merge(rows)

    assert merged == [
        ["Cause", "Corrective action"],
        ["Blocked filter", "Replace the filter and clean the housing before restart."],
    ]


def test_merge_leaves_new_record_rows_intact() -> None:
    rows = [
        ["Cause", "Corrective action"],
        ["Blocked filter", "Replace the filter."],
        ["Loose wire", "Retighten the terminal."],
    ]

    merged = DoclingSparseContinuationRowMerger().merge(rows)

    assert merged == rows


def test_merge_attaches_continuation_ending_in_previously_missing_open_ending() -> None:
    """Regression test: `_OPEN_ENDINGS` used to be missing "was" (and
    "are"/"has"/"have"/"is"/"were"), a genuine drift bug versus the sibling
    troubleshooting merger's copy of this same list. Uses a continuation
    row starting with an uppercase word so the lowercase-start fallback
    signal can't mask the bug -- only the open-ending check can catch it."""
    rows = [
        ["Cause", "Corrective action"],
        ["Sensor fault", "The calibration was"],
        ["", "Verified and corrected by the technician."],
    ]

    merged = DoclingSparseContinuationRowMerger().merge(rows)

    assert merged == [
        ["Cause", "Corrective action"],
        [
            "Sensor fault",
            "The calibration was Verified and corrected by the technician.",
        ],
    ]


def test_merge_attaches_row_with_repeated_anchor_and_continued_description() -> None:
    rows = [
        ["Task", "Description"],
        ["1", "Inspect the pump housing and"],
        ["1", "verify the shaft seal."],
    ]

    merged = DoclingSparseContinuationRowMerger().merge(rows)

    assert merged == [
        ["Task", "Description"],
        ["1", "Inspect the pump housing and verify the shaft seal."],
    ]


def test_merge_uses_vertical_span_evidence_when_text_pattern_is_weak() -> None:
    rows = [
        ["Item", "Notes"],
        ["1", "Sensor fault"],
        ["1", "Replace if necessary"],
    ]

    merged = DoclingSparseContinuationRowMerger().merge(
        rows,
        cell_spans=[
            TableCellSpan(
                row_start=1,
                row_end=2,
                col_start=1,
                col_end=1,
                text="Sensor fault Replace if necessary",
                raw_lines=["Sensor fault", "Replace if necessary"],
            )
        ],
    )

    assert merged == [
        ["Item", "Notes"],
        ["1", "Sensor fault Replace if necessary"],
    ]
