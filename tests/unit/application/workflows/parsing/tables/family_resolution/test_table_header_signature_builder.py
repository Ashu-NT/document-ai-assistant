from src.application.workflows.parsing.tables.family_resolution.table_header_signature_builder import (
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


def test_builder_prefers_child_header_cells_over_inherited_umbrella_spans() -> None:
    builder = TableHeaderSignatureBuilder()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="table",
        rows=[
            ["Technical data", "Technical data"],
            ["Parameter", "Value"],
            ["Voltage", "400V"],
        ],
        column_count=2,
        cell_spans=[
            TableCellSpan(
                row_start=0,
                row_end=1,
                col_start=0,
                col_end=1,
                text="Technical data",
            )
        ],
    )

    signature = builder.build(table)

    assert signature == "technical data > parameter|technical data > value"


def test_builder_strips_generic_continued_marker_from_header_cells() -> None:
    builder = TableHeaderSignatureBuilder()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="table",
        rows=[
            ["Task (continued)", "Interval"],
            ["Replace filter", "Weekly"],
        ],
        column_count=2,
    )

    signature = builder.build(table)

    assert signature == "task|interval"


def test_builder_strips_trailing_page_sequence_marker_from_header_cells() -> None:
    builder = TableHeaderSignatureBuilder()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="table",
        rows=[
            ["Maintenance Schedule (1 of 2)", "Maintenance Schedule (1 of 2)"],
            ["Task", "Notes"],
            ["Check oil", "See annex"],
        ],
        column_count=2,
    )

    signature = builder.build(table)

    assert signature == "maintenance schedule > task|maintenance schedule > notes"


def test_builder_does_not_treat_a_textual_first_data_row_as_a_second_header_row() -> None:
    """Regression test: a maintenance/troubleshooting-style table whose
    first data row is a full text description (not a short label) reads
    just as "label-like" as a genuine header row. Without real merged-
    cell evidence, that row must stay data, not get folded into the
    header signature - otherwise the signature (and the persisted header
    paths shown to the LLM) leak one row's actual content, and two pages
    of the same continued table stop matching because each page's own
    (different) first data row gets compared instead of the real header.
    """
    builder = TableHeaderSignatureBuilder()
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="table",
        rows=[
            ["Task", "Interval", "Notes"],
            ["Check oil level", "Every 6 months", "See gearbox annex"],
            ["Replace filter", "Every 12 months", "Use OEM part"],
        ],
        column_count=3,
    )

    signature = builder.build(table)

    assert signature == "task|interval|notes"
