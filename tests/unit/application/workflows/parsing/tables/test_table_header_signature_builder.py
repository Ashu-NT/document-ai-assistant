from src.application.workflows.parsing.tables.table_header_signature_builder import (
    TableHeaderSignatureBuilder,
)
from src.domain.assets import TableAsset, TableCellSpan


def test_builder_keeps_uniform_umbrella_header_in_the_full_signature() -> None:
    """The primary signature must stay lossless: two unrelated tables
    that share a generic deeper header (e.g. "Parameter | Value") but
    have different umbrella titles must not collapse onto the same
    signature.
    """
    builder = TableHeaderSignatureBuilder()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="table",
        rows=[
            ["Technical data", "", ""],
            ["Parameter", "Compact version", "Remote version"],
            ["Pressure range", "0...10", "0...16"],
        ],
        column_count=3,
    )

    signature = builder.build(table)

    assert signature == (
        "technical data > parameter"
        "|technical data > compact version"
        "|technical data > remote version"
    )


def test_builder_umbrella_collapsed_paths_strips_the_shared_title() -> None:
    builder = TableHeaderSignatureBuilder()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="table",
        rows=[
            ["Technical data", "", ""],
            ["Parameter", "Compact version", "Remote version"],
            ["Pressure range", "0...10", "0...16"],
        ],
        column_count=3,
    )

    collapsed_paths = builder.build_umbrella_collapsed_paths(table)

    assert collapsed_paths == (
        ("parameter",),
        ("compact version",),
        ("remote version",),
    )
    assert builder.umbrella_text(table) == "technical data"


def test_builder_uses_multi_row_paths_when_spans_exist() -> None:
    builder = TableHeaderSignatureBuilder()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="table",
        rows=[
            ["Motor power", "", "Flow"],
            ["kW", "HP", "Q l/min"],
            ["3", "4", "25"],
        ],
        column_count=3,
        cell_spans=[
            TableCellSpan(
                row_start=0,
                row_end=0,
                col_start=0,
                col_end=1,
                text="Motor power",
            ),
            TableCellSpan(
                row_start=0,
                row_end=0,
                col_start=2,
                col_end=2,
                text="Flow",
            ),
        ],
    )

    signature = builder.build(table)

    assert signature == "motor power > kw|motor power > hp|flow > q l/min"
