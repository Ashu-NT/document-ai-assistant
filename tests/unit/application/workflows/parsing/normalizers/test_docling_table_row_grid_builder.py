import pytest

from src.application.workflows.parsing.normalizers.docling_table_row_grid_builder import (
    DoclingTableRowGridBuilder,
)
from src.shared.exceptions import DocumentNormalizationError


def test_build_rows_propagates_vertical_spans_for_repeated_problem_context() -> None:
    builder = DoclingTableRowGridBuilder()

    rows = builder.build_rows(
        [
            {
                "start_row_offset_idx": 0,
                "end_row_offset_idx": 1,
                "start_col_offset_idx": 0,
                "end_col_offset_idx": 1,
                "text": "Problem",
            },
            {
                "start_row_offset_idx": 0,
                "end_row_offset_idx": 1,
                "start_col_offset_idx": 1,
                "end_col_offset_idx": 2,
                "text": "Cause",
            },
            {
                "start_row_offset_idx": 1,
                "end_row_offset_idx": 3,
                "start_col_offset_idx": 0,
                "end_col_offset_idx": 1,
                "text": "Pump locked",
            },
            {
                "start_row_offset_idx": 1,
                "end_row_offset_idx": 2,
                "start_col_offset_idx": 1,
                "end_col_offset_idx": 2,
                "text": "Rust inside pump",
            },
            {
                "start_row_offset_idx": 2,
                "end_row_offset_idx": 3,
                "start_col_offset_idx": 1,
                "end_col_offset_idx": 2,
                "text": "Bearings seized",
            },
        ]
    )

    assert rows == [
        ["Problem", "Cause"],
        ["Pump locked", "Rust inside pump"],
        ["Pump locked", "Bearings seized"],
    ]


def test_build_rows_distributes_compact_interval_headers_across_columns() -> None:
    builder = DoclingTableRowGridBuilder()

    rows = builder.build_rows(
        [
            {
                "start_row_offset_idx": 0,
                "end_row_offset_idx": 1,
                "start_col_offset_idx": 0,
                "end_col_offset_idx": 1,
                "text": "Task",
            },
            {
                "start_row_offset_idx": 0,
                "end_row_offset_idx": 1,
                "start_col_offset_idx": 1,
                "end_col_offset_idx": 4,
                "text": "M S A",
            },
            {
                "start_row_offset_idx": 1,
                "end_row_offset_idx": 2,
                "start_col_offset_idx": 0,
                "end_col_offset_idx": 1,
                "text": "Inspect basket",
            },
            {
                "start_row_offset_idx": 1,
                "end_row_offset_idx": 2,
                "start_col_offset_idx": 1,
                "end_col_offset_idx": 2,
                "text": "X",
            },
        ]
    )

    assert rows == [
        ["Task", "M", "S", "A"],
        ["Inspect basket", "X", "", ""],
    ]


def test_build_rows_fails_loudly_on_an_implausibly_large_malformed_span() -> None:
    """Regression test: a single malformed cell span with a corrupted,
    very large offset must not trigger an unbounded, slow grid
    allocation - it should surface as a clear parsing error instead.
    """
    builder = DoclingTableRowGridBuilder()

    with pytest.raises(DocumentNormalizationError):
        builder.build_rows(
            [
                {
                    "start_row_offset_idx": 0,
                    "end_row_offset_idx": 2_000_000,
                    "start_col_offset_idx": 0,
                    "end_col_offset_idx": 1,
                    "text": "corrupted",
                }
            ]
        )
