from src.domain.assets.table_cell_span import TableCellSpan
from src.domain.assets.table_rows.generic_wrapped_row_table_normalizer import (
    GenericWrappedRowTableNormalizer,
)

_WIDOWED_ROWS = [
    ["Cause", "Corrective action"],
    ["Sensor fault", "The reading was"],
    ["", "verified and corrected."],
]
_WRAP_EVIDENCE = [
    TableCellSpan(
        row_start=1,
        row_end=2,
        col_start=1,
        col_end=1,
        text="The reading was verified and corrected.",
    )
]


def test_normalize_merges_widowed_row_with_cell_span_wrap_evidence() -> None:
    normalized = GenericWrappedRowTableNormalizer().normalize(
        _WIDOWED_ROWS,
        table_category=None,
        chunk_type=None,
        cell_spans=_WRAP_EVIDENCE,
    )

    assert normalized is not None
    assert normalized.headers == ["Cause", "Corrective action"]
    assert normalized.rows == [
        ["Sensor fault", "The reading was verified and corrected."],
    ]


def test_normalize_returns_none_without_cell_span_evidence() -> None:
    """Must not silently duplicate `DoclingSparseContinuationRowMerger`'s
    job without the stronger cell-span signal -- this normalizer only
    fires when Docling itself flagged wrap/span evidence."""
    normalized = GenericWrappedRowTableNormalizer().normalize(
        _WIDOWED_ROWS,
        table_category=None,
        chunk_type=None,
        cell_spans=None,
    )

    assert normalized is None


def test_normalize_returns_none_when_nothing_needs_merging() -> None:
    clean_rows = [
        ["Cause", "Corrective action"],
        ["Blocked filter", "Replace the filter."],
        ["Loose wire", "Retighten the terminal."],
    ]

    normalized = GenericWrappedRowTableNormalizer().normalize(
        clean_rows,
        table_category=None,
        chunk_type=None,
        cell_spans=_WRAP_EVIDENCE,
    )

    assert normalized is None
