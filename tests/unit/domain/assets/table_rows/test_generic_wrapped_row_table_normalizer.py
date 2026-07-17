from src.domain.assets.table_cell_span import TableCellSpan
from src.application.workflows.parsing.tables.normalization.generic_wrapped_row_table_normalizer import (
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


def test_normalize_merges_wrapped_row_with_repeated_anchor_when_span_evidence_exists() -> None:
    rows = [
        ["Task", "Description"],
        ["1", "Inspect the pump housing and"],
        ["1", "verify the shaft seal."],
    ]

    normalized = GenericWrappedRowTableNormalizer().normalize(
        rows,
        table_category=None,
        chunk_type=None,
        cell_spans=_WRAP_EVIDENCE,
    )

    assert normalized is not None
    assert normalized.headers == ["Task", "Description"]
    assert normalized.rows == [["1", "Inspect the pump housing and verify the shaft seal."]]


def test_normalize_uses_vertical_span_evidence_when_text_pattern_is_weak() -> None:
    rows = [
        ["Item", "Notes"],
        ["1", "Sensor fault"],
        ["1", "Replace if necessary"],
    ]

    normalized = GenericWrappedRowTableNormalizer().normalize(
        rows,
        table_category=None,
        chunk_type=None,
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

    assert normalized is not None
    assert normalized.headers == ["Item", "Notes"]
    assert normalized.rows == [["1", "Sensor fault Replace if necessary"]]
