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
