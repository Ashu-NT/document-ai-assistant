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


def test_build_rows_reconstructs_parallel_toc_lanes_when_cell_geometry_exists() -> None:
    builder = DoclingTableRowGridBuilder()

    def make_cell(row, col, text, x1, x2):
        return {
            "start_row_offset_idx": row,
            "end_row_offset_idx": row + 1,
            "start_col_offset_idx": col,
            "end_col_offset_idx": col + 1,
            "text": text,
            "prov": [
                {
                    "page_no": 1,
                    "bbox": {"x1": x1, "y1": 100 + (row * 20), "x2": x2, "y2": 118 + (row * 20)},
                }
            ],
        }

    rows = builder.build_rows(
        [
            make_cell(0, 0, "1 Preface", 40, 320),
            make_cell(0, 1, "11", 330, 360),
            make_cell(1, 0, "1.1 Introduction", 40, 320),
            make_cell(1, 1, "12", 330, 360),
            make_cell(2, 0, "2 Safety", 40, 320),
            make_cell(2, 1, "15", 330, 360),
            make_cell(0, 2, "6 Maintenance", 610, 900),
            make_cell(0, 3, "67", 910, 940),
            make_cell(1, 2, "7 Operating Instructions", 610, 900),
            make_cell(1, 3, "69", 910, 940),
            make_cell(2, 2, "7.2 Troubleshooting", 610, 900),
            make_cell(2, 3, "81", 910, 940),
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["1.1", "Introduction", "12"],
        ["2", "Safety", "15"],
        ["6", "Maintenance", "67"],
        ["7", "Operating Instructions", "69"],
        ["7.2", "Troubleshooting", "81"],
    ]


def test_build_reconstruction_preserves_parallel_specification_streams() -> None:
    builder = DoclingTableRowGridBuilder()

    def make_cell(row, col, text, x1, x2):
        return {
            "start_row_offset_idx": row,
            "end_row_offset_idx": row + 1,
            "start_col_offset_idx": col,
            "end_col_offset_idx": col + 1,
            "text": text,
            "prov": [
                {
                    "page_no": 1,
                    "bbox": {"x1": x1, "y1": 100 + (row * 20), "x2": x2, "y2": 118 + (row * 20)},
                }
            ],
        }

    reconstruction = builder.build_reconstruction(
        builder.cell_candidate_builder.build(
            [
                make_cell(0, 0, "Parameter", 40, 250),
                make_cell(0, 1, "Value", 260, 330),
                make_cell(1, 0, "Voltage", 40, 250),
                make_cell(1, 1, "400V", 260, 330),
                make_cell(0, 2, "Parameter", 620, 830),
                make_cell(0, 3, "Value", 840, 910),
                make_cell(1, 2, "Frequency", 620, 830),
                make_cell(1, 3, "50Hz", 840, 910),
            ]
        )
    )

    assert reconstruction.parallel_stream_rows == [
        [["Parameter", "Value"], ["Voltage", "400V"]],
        [["Parameter", "Value"], ["Frequency", "50Hz"]],
    ]
    assert reconstruction.local_reading_order == "left_to_right_top_to_bottom"
    assert reconstruction.rows == [
        ["Parameter", "Value"],
        ["Voltage", "400V"],
        ["Frequency", "50Hz"],
    ]


def test_build_reconstruction_page_lane_count_is_a_pure_pass_through() -> None:
    builder = DoclingTableRowGridBuilder()

    def make_cell(row, col, text, x1, x2):
        return {
            "start_row_offset_idx": row,
            "end_row_offset_idx": row + 1,
            "start_col_offset_idx": col,
            "end_col_offset_idx": col + 1,
            "text": text,
            "prov": [
                {
                    "page_no": 1,
                    "bbox": {"x1": x1, "y1": 100 + (row * 20), "x2": x2, "y2": 118 + (row * 20)},
                }
            ],
        }

    spans = builder.cell_candidate_builder.build(
        [
            make_cell(0, 0, "Parameter", 40, 250),
            make_cell(0, 1, "Value", 260, 330),
            make_cell(1, 0, "Voltage", 40, 250),
            make_cell(1, 1, "400V", 260, 330),
            make_cell(0, 2, "Parameter", 620, 830),
            make_cell(0, 3, "Value", 840, 910),
            make_cell(1, 2, "Frequency", 620, 830),
            make_cell(1, 3, "50Hz", 840, 910),
        ]
    )

    without_hint = builder.build_reconstruction(spans)
    with_mismatched_hint = builder.build_reconstruction(spans, page_lane_count=1)

    assert without_hint.rows == with_mismatched_hint.rows
    assert without_hint.parallel_stream_rows == with_mismatched_hint.parallel_stream_rows
