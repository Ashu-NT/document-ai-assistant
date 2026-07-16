from src.application.workflows.parsing.normalizers.docling_sparse_continuation_row_merger import (
    DoclingSparseContinuationRowMerger,
)


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
