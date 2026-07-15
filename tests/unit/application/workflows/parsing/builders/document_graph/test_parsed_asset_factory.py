from src.application.workflows.parsing.builders.document_graph.parsed_asset_factory import (
    ParsedAssetFactory,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.tables.structure.table_header_path_builder import (
    TableHeaderPathBuilder,
)
from src.domain.common import ElementType
from src.shared.ids import IdGenerator


def _parsed_table_element(**metadata_overrides: object) -> CanonicalElement:
    metadata = {
        "table_rows": [
            ["Parameter", "", "Value"],
            ["Bore", "", "25mm"],
        ],
        "table_cell_spans": [
            {"row_start": 0, "row_end": 0, "col_start": 0, "col_end": 0, "text": "Parameter"},
            {"row_start": 0, "row_end": 0, "col_start": 1, "col_end": 1, "text": ""},
            {"row_start": 0, "row_end": 0, "col_start": 2, "col_end": 2, "text": "Value"},
        ],
        "row_count": 2,
        "column_count": 3,
    }
    metadata.update(metadata_overrides)
    return CanonicalElement(
        element_id="el_table_1",
        document_id="doc_1",
        element_type=ElementType.TABLE,
        metadata=metadata,
    )


def test_build_table_asset_drops_globally_empty_column_and_remaps_cell_spans() -> None:
    factory = ParsedAssetFactory(IdGenerator())

    _, table = factory.build_table_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=_parsed_table_element(),
    )

    assert table.rows == [["Parameter", "Value"], ["Bore", "25mm"]]
    assert table.column_count == 2
    span_columns = {(span.col_start, span.col_end) for span in table.cell_spans}
    assert (0, 0) in span_columns
    assert (1, 1) in span_columns
    assert all(col_start <= 1 and col_end <= 1 for col_start, col_end in span_columns)


def test_build_table_asset_drops_span_that_lived_entirely_in_a_dropped_column() -> None:
    factory = ParsedAssetFactory(IdGenerator())

    _, table = factory.build_table_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=_parsed_table_element(),
    )

    assert len(table.cell_spans) == 2
    assert {span.text for span in table.cell_spans} == {"Parameter", "Value"}


def test_build_table_asset_leaves_geometry_untouched_when_no_column_is_dropped() -> None:
    factory = ParsedAssetFactory(IdGenerator())
    parsed_element = _parsed_table_element(
        table_rows=[["Parameter", "Value"], ["Bore", "25mm"]],
        table_cell_spans=[
            {"row_start": 0, "row_end": 0, "col_start": 0, "col_end": 0, "text": "Parameter"},
            {"row_start": 0, "row_end": 0, "col_start": 1, "col_end": 1, "text": "Value"},
        ],
        column_count=2,
    )

    _, table = factory.build_table_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=parsed_element,
    )

    assert table.column_count == 2
    assert [(s.col_start, s.col_end) for s in table.cell_spans] == [(0, 0), (1, 1)]


def test_header_path_builder_resolves_correct_header_after_column_drop() -> None:
    factory = ParsedAssetFactory(IdGenerator())
    _, table = factory.build_table_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=_parsed_table_element(),
    )

    paths = TableHeaderPathBuilder().build_paths(table)

    assert paths == (("parameter",), ("value",))


def test_build_table_asset_rehydrates_parallel_stream_rows() -> None:
    factory = ParsedAssetFactory(IdGenerator())
    parsed_element = _parsed_table_element(
        table_rows=[["Parameter", "Value"], ["Voltage", "400V"]],
        table_parallel_stream_rows=[
            [["Parameter", "Value"], ["Voltage", "400V"]],
            [["Parameter", "Value"], ["Frequency", "50Hz"]],
        ],
        column_count=2,
    )

    _, table = factory.build_table_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=parsed_element,
    )

    assert table.parallel_stream_rows == [
        [["Parameter", "Value"], ["Voltage", "400V"]],
        [["Parameter", "Value"], ["Frequency", "50Hz"]],
    ]
