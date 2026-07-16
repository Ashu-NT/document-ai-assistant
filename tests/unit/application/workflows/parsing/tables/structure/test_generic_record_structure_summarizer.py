import pytest

from src.application.workflows.parsing.tables.structure.generic_record_structure_summarizer import (
    GenericRecordStructureSummarizer,
)
from src.application.workflows.shared.table_shape import TableShape
from src.domain.assets import TableAsset, TableCellSpan


def _make_table(
    *,
    rows: list[list[str]],
    cell_spans: list[TableCellSpan] | None = None,
) -> TableAsset:
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="",
        rows=rows,
        cell_spans=cell_spans or [],
    )


def test_summarize_returns_none_for_fewer_than_two_rows() -> None:
    table = _make_table(rows=[["Part", "Description"]])

    assert GenericRecordStructureSummarizer().summarize(table) is None


def test_summarize_returns_none_when_no_data_rows_remain_after_the_header() -> None:
    table = _make_table(
        rows=[["Spec", "Spec"], ["A", "B"]],
        cell_spans=[
            TableCellSpan(row_start=0, row_end=0, col_start=0, col_end=1, text="Spec"),
        ],
    )

    assert GenericRecordStructureSummarizer().summarize(table) is None


def test_summarize_returns_none_for_single_column_table() -> None:
    table = _make_table(rows=[["Header"], ["Data 1"], ["Data 2"]])

    assert GenericRecordStructureSummarizer().summarize(table) is None


def test_summarize_returns_none_when_headers_lack_alpha_signal() -> None:
    table = _make_table(rows=[["1", "2"], ["a", "b"], ["c", "d"]])

    assert GenericRecordStructureSummarizer().summarize(table) is None


def test_summarize_produces_record_table_summary_with_expected_quality_score() -> None:
    table = _make_table(
        rows=[
            ["Part", "Description", "Quantity"],
            ["A1", "Bolt", "10"],
            ["A2", "Nut", "5"],
        ]
    )

    summary = GenericRecordStructureSummarizer().summarize(table)

    assert summary is not None
    assert summary.table_shape == TableShape.RECORD_TABLE
    assert summary.header_paths == [["part"], ["description"], ["quantity"]]
    assert summary.axis_summary == {
        "row_axis": "record",
        "column_axis": "attribute",
        "value_axis": "cell_value",
    }
    assert summary.quality_score == pytest.approx(0.80)


def test_summarize_scores_lower_without_the_two_data_rows_bonus() -> None:
    table = _make_table(
        rows=[
            ["Part", "Description", "Quantity"],
            ["A1", "Bolt", "10"],
        ]
    )

    summary = GenericRecordStructureSummarizer().summarize(table)

    assert summary is not None
    assert summary.quality_score == pytest.approx(0.70)
