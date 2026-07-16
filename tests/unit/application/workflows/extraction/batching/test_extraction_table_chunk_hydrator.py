from src.application.workflows.extraction.batching.extraction_table_chunk_hydrator import (
    hydrate_table_chunks,
)
from src.domain.assets import TableAsset
from src.domain.common import ChunkType
from src.domain.document import DocumentChunk


def test_hydrate_table_chunks_uses_single_merged_family_table_payload() -> None:
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
        family_index=1,
        family_total=2,
        table_category="technical_data_table",
        table_shape="record_table",
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
        family_index=2,
        family_total=2,
        table_category="technical_data_table",
        table_shape="record_table",
        header_paths=[["component"], ["manufacturer"], ["serial number"]],
        axis_summary={"row_axis": "record", "column_axis": "attribute"},
    )
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        section_id=None,
        content="partial table",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        table_ids=[first.table_id],
        logical_table_family_id="family_001",
        table_category="technical_data_table",
    )

    hydrated = hydrate_table_chunks(
        chunks=[chunk],
        tables={first.table_id: first, second.table_id: second},
    )

    assert len(hydrated) == 1
    assert hydrated[0].table_ids == ["table_001", "table_002"]
    assert hydrated[0].table_row_start == 1
    assert hydrated[0].table_row_end == 3
    assert "Table shape: record_table" in hydrated[0].content
    assert "Header paths: component | manufacturer | serial number" in hydrated[0].content
    assert "Row 1: component=Pump | manufacturer=Calpeda | serial number=SN-001" in hydrated[
        0
    ].content
    assert "Row 2: component=Motor | manufacturer=ABB | serial number=SN-002" in hydrated[
        0
    ].content
