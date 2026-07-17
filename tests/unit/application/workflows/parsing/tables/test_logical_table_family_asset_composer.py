from src.application.workflows.parsing.tables.families import (
    LogicalTableFamilyAssetComposer,
    LogicalTableFamilyRowMerger,
)
from src.domain.assets import TableAsset


def test_row_merger_drops_repeated_multi_row_header_block_for_compatible_family() -> None:
    first = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="technical data page 1",
        rows=[
            ["Technical data", "Technical data", "Technical data"],
            ["Component", "Manufacturer", "Serial number"],
            ["Pump", "Calpeda", "SN-001"],
        ],
    )
    second = TableAsset(
        table_id="table_002",
        document_id="doc_001",
        markdown="technical data page 2",
        rows=[
            ["Technical data", "Technical data", "Technical data"],
            ["Component", "Manufacturer", "Serial number"],
            ["Motor", "ABB", "SN-002"],
        ],
    )

    merged = LogicalTableFamilyRowMerger().merge_tables([first, second])

    assert merged == [
        ["Technical data", "Technical data", "Technical data"],
        ["Component", "Manufacturer", "Serial number"],
        ["Pump", "Calpeda", "SN-001"],
        ["Motor", "ABB", "SN-002"],
    ]


def test_row_merger_drops_repeated_multi_row_header_block_in_plain_row_groups() -> None:
    merged = LogicalTableFamilyRowMerger().merge_row_groups(
        [
            [
                ["Technical data", "Technical data", "Technical data"],
                ["Component", "Manufacturer", "Serial number"],
                ["Pump", "Calpeda", "SN-001"],
            ],
            [
                ["Technical data", "Technical data", "Technical data"],
                ["Component", "Manufacturer", "Serial number"],
                ["Motor", "ABB", "SN-002"],
            ],
        ]
    )

    assert merged == [
        ["Technical data", "Technical data", "Technical data"],
        ["Component", "Manufacturer", "Serial number"],
        ["Pump", "Calpeda", "SN-001"],
        ["Motor", "ABB", "SN-002"],
    ]


def test_row_merger_matches_plain_row_group_continuations_with_minor_umbrella_variation() -> None:
    merged = LogicalTableFamilyRowMerger().merge_row_groups(
        [
            [
                ["Maintenance Schedule (1 of 2)", "Maintenance Schedule (1 of 2)"],
                ["Task", "Notes"],
                ["Check oil", "See annex"],
            ],
            [
                ["Maintenance Schedule (2 of 2)", "Maintenance Schedule (2 of 2)"],
                ["Task", "Notes"],
                ["Replace filter", "Use OEM part"],
            ],
        ]
    )

    assert merged == [
        ["Maintenance Schedule (1 of 2)", "Maintenance Schedule (1 of 2)"],
        ["Task", "Notes"],
        ["Check oil", "See annex"],
        ["Replace filter", "Use OEM part"],
    ]


def test_asset_composer_builds_single_family_table_with_merged_rows_and_metadata() -> None:
    first = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="technical data page 1",
        rows=[
            ["Technical data", "Technical data", "Technical data"],
            ["Component", "Manufacturer", "Serial number"],
            ["Pump", "Calpeda", "SN-001"],
        ],
        logical_table_family_id="family_001",
        table_category="technical_data_table",
        table_shape="record_table",
        table_structure_quality=0.82,
        header_paths=[["component"], ["manufacturer"], ["serial number"]],
        axis_summary={"row_axis": "record", "column_axis": "attribute"},
    )
    second = TableAsset(
        table_id="table_002",
        document_id="doc_001",
        markdown="technical data page 2",
        rows=[
            ["Technical data", "Technical data", "Technical data"],
            ["Component", "Manufacturer", "Serial number"],
            ["Motor", "ABB", "SN-002"],
        ],
        logical_table_family_id="family_001",
        table_category="technical_data_table",
        header_paths=[["manufacturer"], ["serial number"]],
    )

    composed = LogicalTableFamilyAssetComposer().compose([first, second])

    assert composed is not None
    assert composed.table_id == "family_001"
    assert composed.logical_table_family_id == "family_001"
    assert composed.family_total == 2
    assert composed.rows == [
        ["Technical data", "Technical data", "Technical data"],
        ["Component", "Manufacturer", "Serial number"],
        ["Pump", "Calpeda", "SN-001"],
        ["Motor", "ABB", "SN-002"],
    ]
    assert composed.table_category == "technical_data_table"
    assert composed.table_shape == "record_table"
    assert composed.table_structure_quality == 0.82
    assert composed.header_paths == [
        ["component"],
        ["manufacturer"],
        ["serial number"],
    ]
