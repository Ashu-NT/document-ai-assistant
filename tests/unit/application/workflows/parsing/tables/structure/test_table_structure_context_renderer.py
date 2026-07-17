from src.application.workflows.parsing.tables.structure.table_structure_context_renderer import (
    TableStructureContextRenderer,
)
from src.domain.assets import TableAsset, TableParallelStream


def test_renderer_includes_parallel_stream_details() -> None:
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="parallel",
        rows=[["Parameter", "Value"], ["Voltage", "400V"]],
        parallel_stream_rows=[
            [["Parameter", "Value"], ["Voltage", "400V"]],
            [["Parameter", "Value"], ["Frequency", "50Hz"]],
        ],
        parallel_stream_descriptors=[
            TableParallelStream(
                stream_index=1,
                source_row_start=0,
                source_row_end=1,
                source_col_start=0,
                source_col_end=1,
                row_count=2,
                column_count=2,
                page_number=6,
            ),
            TableParallelStream(
                stream_index=2,
                source_row_start=0,
                source_row_end=1,
                source_col_start=2,
                source_col_end=3,
                row_count=2,
                column_count=2,
                page_number=6,
            ),
        ],
        local_reading_order="left_to_right_top_to_bottom",
    )

    rendered = TableStructureContextRenderer().render(table)

    assert rendered is not None
    assert "Parallel streams: 2 (left_to_right_top_to_bottom)" in rendered
    assert "Left stream, page=6, rows=2, columns=2" in rendered
    assert "Right stream, page=6, rows=2, columns=2" in rendered
