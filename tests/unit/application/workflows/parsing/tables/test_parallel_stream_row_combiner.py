from src.application.workflows.parsing.tables.normalization.parallel_stream_row_combiner import (
    ParallelStreamRowCombiner,
)
from src.application.workflows.parsing.tables.normalization.table_row_semantic_normalizer import (
    TableRowSemanticNormalizer,
)
from src.domain.assets import TableAsset


def test_combiner_merges_parallel_streams_with_header_alias_and_extra_notes_column() -> None:
    combined = ParallelStreamRowCombiner().combine(
        [
            [["Part Number", "Description"], ["HP-001", "Filter"]],
            [["Part No.", "Description", "Notes"], ["HP-002", "Gasket", "Use OEM parts"]],
        ]
    )

    assert combined == [
        ["Part Number", "Description", "Notes"],
        ["HP-001", "Filter", ""],
        ["HP-002", "Gasket", "Use OEM parts"],
    ]


def test_table_row_semantic_normalizer_combines_parallel_streams_with_optional_notes_column() -> None:
    table = TableAsset(
        table_id="table_parallel_1",
        document_id="doc_1",
        markdown="maintenance schedule",
        table_category="maintenance_interval_table",
        rows=[["Task", "D", "W"], ["Inspect pump", "x", ""], ["Replace seal", "", "x"]],
        parallel_stream_rows=[
            [["Task", "D", "W"], ["Inspect pump", "x", ""]],
            [["Task", "D", "W", "Notes"], ["Replace seal", "", "x", "Use OEM parts"]],
        ],
    )

    updated = TableRowSemanticNormalizer().normalize(table)

    assert updated is True
    assert table.parallel_stream_rows == [
        [["Task", "Daily", "Weekly"], ["Inspect pump", "x", ""]],
        [["Task", "Daily", "Weekly", "Notes"], ["Replace seal", "", "x", "Use OEM parts"]],
    ]
    assert table.rows == [
        ["Task", "Daily", "Weekly", "Notes"],
        ["Inspect pump", "x", "", ""],
        ["Replace seal", "", "x", "Use OEM parts"],
    ]


def test_combiner_merges_parallel_streams_with_shared_task_anchor_and_distinct_interval_columns() -> None:
    combined = ParallelStreamRowCombiner().combine(
        [
            [["Task", "D", "W"], ["Inspect pump", "x", ""]],
            [["Task", "Q", "A", "Notes"], ["Inspect pump", "", "x", "Use OEM parts"]],
        ]
    )

    assert combined == [
        ["Task", "D", "W", "Q", "A", "Notes"],
        ["Inspect pump", "x", "", "", "", ""],
        ["Inspect pump", "", "", "", "x", "Use OEM parts"],
    ]


def test_combiner_rejects_single_non_leading_anchor_match() -> None:
    combined = ParallelStreamRowCombiner().combine(
        [
            [["Description", "Qty"], ["Filter", "1"]],
            [["Part Number", "Description"], ["HP-001", "Filter"]],
        ]
    )

    assert combined is None
