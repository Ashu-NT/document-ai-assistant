from src.application.workflows.parsing.builders.document_graph.parsed_assets.parsed_asset_factory import (
    ParsedAssetFactory,
)
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.application.workflows.parsing.tables.structure.table_header_path_builder import (
    TableHeaderPathBuilder,
)
from src.domain.common import ElementType
from src.shared.ids import IdGenerator


def _parsed_table_element(**metadata_overrides: object) -> ParsedCanonicalElement:
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
    return ParsedCanonicalElement(
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


def test_build_table_asset_populates_layout_fields_from_metadata() -> None:
    factory = ParsedAssetFactory(IdGenerator())
    parsed_element = _parsed_table_element(
        layout_region_id="page_3:lane_1",
        layout_region_role="body",
        layout_lane_index="1",
        layout_lane_count="2",
        page_orientation="landscape",
    )

    _, table = factory.build_table_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=parsed_element,
    )

    assert table.layout_region_id == "page_3:lane_1"
    assert table.layout_region_role == "body"
    assert table.layout_lane_index == 1
    assert table.layout_lane_count == 2
    assert table.page_orientation == "landscape"


def test_build_table_asset_defaults_layout_fields_to_none_when_absent() -> None:
    factory = ParsedAssetFactory(IdGenerator())

    _, table = factory.build_table_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=_parsed_table_element(),
    )

    assert table.layout_region_id is None
    assert table.layout_region_role is None
    assert table.layout_lane_index is None
    assert table.layout_lane_count is None
    assert table.page_orientation is None


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


def test_build_table_asset_rehydrates_parallel_stream_descriptors() -> None:
    factory = ParsedAssetFactory(IdGenerator())
    parsed_element = _parsed_table_element(
        table_rows=[["Parameter", "Value"], ["Voltage", "400V"]],
        table_parallel_stream_rows=[
            [["Parameter", "Value"], ["Voltage", "400V"]],
            [["Parameter", "Value"], ["Frequency", "50Hz"]],
        ],
        table_parallel_stream_descriptors=[
            {
                "stream_index": 1,
                "source_row_start": 0,
                "source_row_end": 1,
                "source_col_start": 0,
                "source_col_end": 1,
                "row_count": 2,
                "column_count": 2,
                "page_number": 4,
            },
            {
                "stream_index": 2,
                "source_row_start": 0,
                "source_row_end": 1,
                "source_col_start": 2,
                "source_col_end": 3,
                "row_count": 2,
                "column_count": 2,
                "page_number": 4,
            },
        ],
        column_count=2,
    )

    _, table = factory.build_table_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=parsed_element,
    )

    assert [item.stream_index for item in table.parallel_stream_descriptors] == [1, 2]
    assert [item.page_number for item in table.parallel_stream_descriptors] == [4, 4]


def _parsed_form_element(**metadata_overrides: object) -> ParsedCanonicalElement:
    metadata = {
        "form_fields": [
            {
                "label": "key",
                "key_text": "Model",
                "value_text": "HP-001",
                "cell_id": 0,
            }
        ],
        "caption": "Equipment identification form",
    }
    metadata.update(metadata_overrides)
    return ParsedCanonicalElement(
        element_id="el_form_1",
        document_id="doc_1",
        element_type=ElementType.FORM,
        metadata=metadata,
    )


def test_build_form_asset_populates_fields_from_metadata() -> None:
    factory = ParsedAssetFactory(IdGenerator())

    _, form = factory.build_form_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=_parsed_form_element(),
    )

    assert len(form.fields) == 1
    assert form.fields[0].label == "key"
    assert form.fields[0].key_text == "Model"
    assert form.fields[0].value_text == "HP-001"
    assert form.fields[0].cell_id == 0
    assert form.metadata.caption == "Equipment identification form"


def test_build_form_asset_drops_fields_with_no_key_or_value_text() -> None:
    factory = ParsedAssetFactory(IdGenerator())

    _, form = factory.build_form_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=_parsed_form_element(
            form_fields=[
                {"label": "key", "key_text": None, "value_text": None, "cell_id": 1}
            ]
        ),
    )

    assert form.fields == []


def test_build_form_asset_defaults_to_empty_fields_when_missing() -> None:
    factory = ParsedAssetFactory(IdGenerator())

    _, form = factory.build_form_asset(
        document_id="doc_1",
        parent_section_id=None,
        parsed_element=_parsed_form_element(form_fields=None),
    )

    assert form.fields == []
    assert form.has_fields() is False
