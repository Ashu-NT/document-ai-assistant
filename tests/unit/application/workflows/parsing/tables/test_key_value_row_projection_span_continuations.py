from src.application.workflows.parsing.tables.normalization.key_value_row_projection import (
    project_key_value_rows,
)
from src.application.workflows.parsing.tables.normalization.specification_key_value_table_normalizer import (
    SpecificationKeyValueTableNormalizer,
)
from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.domain.assets.table_cell_span import TableCellSpan


def test_project_key_value_rows_merges_span_backed_repeated_label_rows() -> None:
    projected = project_key_value_rows(
        [
            ["Accuracy", "≤ 0.4%"],
            ["Accuracy", "Reading basis"],
            ["Weight", "120"],
            ["Weight", "Kilograms"],
        ],
        row_canonicalizer=TableRowCanonicalizer(),
        cell_spans=[
                TableCellSpan(
                    row_start=0,
                    row_end=1,
                    col_start=1,
                    col_end=1,
                    text="≤ 0.4% Reading basis",
                    raw_lines=["≤ 0.4%", "Reading basis"],
                ),
                TableCellSpan(
                    row_start=2,
                    row_end=3,
                    col_start=1,
                    col_end=1,
                    text="120 Kilograms",
                    raw_lines=["120", "Kilograms"],
                ),
            ],
        )

    assert projected is not None
    assert projected.headers == ["Label", "Value"]
    assert projected.rows == [
        ["Accuracy", "≤ 0.4% Reading basis"],
        ["Weight", "120 Kilograms"],
    ]


def test_specification_normalizer_uses_span_backed_key_value_merge() -> None:
    normalized = SpecificationKeyValueTableNormalizer().normalize(
        [
            ["Accuracy", "≤ 0.4%"],
            ["Accuracy", "Reading basis"],
            ["Weight", "120"],
            ["Weight", "Kilograms"],
        ],
        table_category="technical_data_table",
        chunk_type=None,
        cell_spans=[
                TableCellSpan(
                    row_start=0,
                    row_end=1,
                    col_start=1,
                    col_end=1,
                    text="≤ 0.4% Reading basis",
                ),
                TableCellSpan(
                    row_start=2,
                    row_end=3,
                    col_start=1,
                    col_end=1,
                    text="120 Kilograms",
                ),
            ],
        )

    assert normalized is not None
    assert normalized.headers == ["Label", "Value"]
    assert normalized.rows == [
        ["Accuracy", "≤ 0.4% Reading basis"],
        ["Weight", "120 Kilograms"],
    ]
