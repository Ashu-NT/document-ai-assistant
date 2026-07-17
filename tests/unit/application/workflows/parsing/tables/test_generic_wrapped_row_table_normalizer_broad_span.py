from src.application.workflows.parsing.tables.normalization.generic_wrapped_row_table_normalizer import (
    GenericWrappedRowTableNormalizer,
)
from src.application.workflows.parsing.tables.rows.span_aware_row_continuation_resolver import (
    SpanAwareRowContinuationResolver,
)
from src.domain.assets.table_cell_span import TableCellSpan


def test_normalize_merges_rows_when_broad_span_covers_multiple_changed_columns() -> None:
    normalized = GenericWrappedRowTableNormalizer().normalize(
        [
            ["Item", "Fault", "Action", "Notes"],
            [
                "1",
                "Engine speed",
                "Reduce load and inspect",
                "Record alarm in",
            ],
            [
                "1",
                "too low",
                "fuel supply immediately",
                "maintenance log",
            ],
        ],
        table_category="general_table",
        chunk_type=None,
        cell_spans=[
            TableCellSpan(
                row_start=1,
                row_end=2,
                col_start=1,
                col_end=3,
                text=(
                    "Engine speed too low Reduce load and inspect fuel supply "
                    "immediately Record alarm in maintenance log"
                ),
            )
        ],
    )

    assert normalized is not None
    assert normalized.headers == ["Item", "Fault", "Action", "Notes"]
    assert normalized.rows == [
        [
            "1",
            "Engine speed too low",
            "Reduce load and inspect fuel supply immediately",
            "Record alarm in maintenance log",
        ]
    ]


def test_span_aware_resolver_rejects_broad_span_that_misses_a_changed_column() -> None:
    resolved = SpanAwareRowContinuationResolver().resolve(
        ["1", "Engine speed", "Reduce load and inspect", "Record alarm in"],
        ["1", "too low", "fuel supply immediately", "maintenance log"],
        previous_row_index=1,
        current_row_index=2,
        cell_spans=[
            TableCellSpan(
                row_start=1,
                row_end=2,
                col_start=1,
                col_end=2,
                text=(
                    "Engine speed too low Reduce load and inspect fuel supply "
                    "immediately"
                ),
            )
        ],
    )

    assert resolved == []
