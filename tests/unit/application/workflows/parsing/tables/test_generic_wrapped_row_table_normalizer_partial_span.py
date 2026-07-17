from src.application.workflows.parsing.tables.normalization.generic_wrapped_row_table_normalizer import (
    GenericWrappedRowTableNormalizer,
)
from src.domain.assets.table_cell_span import TableCellSpan


def test_normalize_merges_rows_when_one_changed_column_has_span_proof_and_others_are_textual_continuations() -> None:
    normalized = GenericWrappedRowTableNormalizer().normalize(
        [
            ["Item", "Cause", "Action", "Notes"],
            ["1", "Filter housing is", "Tighten the cover and", "Recheck after"],
            ["1", "damaged", "inspect the seal.", "startup in maintenance log"],
        ],
        table_category="general_table",
        chunk_type=None,
        cell_spans=[
            TableCellSpan(
                row_start=1,
                row_end=2,
                col_start=1,
                col_end=1,
                text="Filter housing is damaged",
                raw_lines=["Filter housing is", "damaged"],
            )
        ],
    )

    assert normalized is not None
    assert normalized.headers == ["Item", "Cause", "Action", "Notes"]
    assert normalized.rows == [
        [
            "1",
            "Filter housing is damaged",
            "Tighten the cover and inspect the seal.",
            "Recheck after startup in maintenance log",
        ]
    ]


def test_normalize_does_not_merge_without_any_span_proof_even_if_textual_continuations_exist() -> None:
    normalized = GenericWrappedRowTableNormalizer().normalize(
        [
            ["Item", "Cause", "Action", "Notes"],
            ["1", "Filter housing is", "Tighten the cover and", "Recheck after"],
            ["1", "damaged", "inspect the seal.", "startup in maintenance log"],
        ],
        table_category="general_table",
        chunk_type=None,
        cell_spans=None,
    )

    assert normalized is None
