from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.table_fragment_builder import (
    TableFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ChunkType, ElementType, ParserMetadata
from src.domain.elements import CanonicalElement


def _make_builder() -> TableFragmentBuilder:
    text_splitter = ChunkTextSplitter()
    return TableFragmentBuilder(
        text_splitter=text_splitter,
        include_table_context=False,
        asset_context_resolver=AssetContextResolver(
            text_splitter=text_splitter,
            asset_context_window=0,
            asset_context_max_tokens=0,
            element_contributes_to_chunk=lambda _element: True,
        ),
    )


def _make_table_element(*, table_category: str) -> CanonicalElement:
    return CanonicalElement(
        element_id="el_table_1",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text="| Parameter | Value |",
        parser_metadata=ParserMetadata(
            parser_name="docling",
            extra={
                "markdown": "| Parameter | Value |",
                "table_category": table_category,
            },
        ),
    )


def test_table_chunk_type_uses_maintenance_interval_category() -> None:
    chunk_type = _make_builder().table_chunk_type(
        _make_table_element(table_category="maintenance_interval_table"),
        "| Task | Daily |",
    )

    assert chunk_type == ChunkType.MAINTENANCE_INTERVAL


def test_table_chunk_type_uses_technical_data_category() -> None:
    chunk_type = _make_builder().table_chunk_type(
        _make_table_element(table_category="technical_data_table"),
        "| Parameter | Value |",
    )

    assert chunk_type == ChunkType.TECHNICAL_SPECIFICATION


def test_table_chunk_type_uses_operation_reference_category() -> None:
    chunk_type = _make_builder().table_chunk_type(
        _make_table_element(table_category="operation_reference_table"),
        "| Operating key | Meaning |",
    )

    assert chunk_type == ChunkType.OPERATION_INSTRUCTION


def _make_structured_table_element(
    *,
    element_id: str = "el_table_1",
    table_shape: str | None = None,
    table_structure_quality: float | None = None,
    header_paths: list | None = None,
    axis_summary: dict | None = None,
) -> CanonicalElement:
    extra: dict = {"markdown": "| Parameter | Value |"}
    if table_shape is not None:
        extra["table_shape"] = table_shape
    if table_structure_quality is not None:
        extra["table_structure_quality"] = table_structure_quality
    if header_paths is not None:
        extra["table_header_paths_json"] = header_paths
    if axis_summary is not None:
        extra["table_axis_summary"] = axis_summary
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text="| Parameter | Value |",
        parser_metadata=ParserMetadata(parser_name="docling", extra=extra),
    )


def test_table_metadata_forwards_shape_quality_header_paths_and_axis_summary() -> None:
    element = _make_structured_table_element(
        table_shape="specification_matrix",
        table_structure_quality=0.87,
        header_paths=[["Parameter"], ["Value"]],
        axis_summary={"rows": "parameter", "columns": "value"},
    )

    metadata = TableFragmentBuilder.table_metadata(element)

    assert metadata["table_shape"] == "specification_matrix"
    assert metadata["table_structure_quality"] == 0.87
    assert metadata["header_paths"] == [["Parameter"], ["Value"]]
    assert metadata["axis_summary"] == {"rows": "parameter", "columns": "value"}


def test_table_metadata_defaults_the_four_fields_when_absent() -> None:
    element = _make_structured_table_element()

    metadata = TableFragmentBuilder.table_metadata(element)

    assert metadata["table_shape"] is None
    assert metadata["table_structure_quality"] is None
    assert metadata["header_paths"] == []
    assert metadata["axis_summary"] == {}


def test_merge_family_table_metadata_takes_first_non_null_shape_and_quality() -> None:
    elements = [
        _make_structured_table_element(element_id="el_1"),
        _make_structured_table_element(
            element_id="el_2",
            table_shape="performance_curve_matrix",
            table_structure_quality=0.75,
        ),
        _make_structured_table_element(
            element_id="el_3",
            table_shape="record_table",
            table_structure_quality=0.5,
        ),
    ]

    merged = TableFragmentBuilder.merge_family_table_metadata(elements)

    assert merged["table_shape"] == "performance_curve_matrix"
    assert merged["table_structure_quality"] == 0.75


def test_merge_family_table_metadata_unions_header_paths_and_axis_summary() -> None:
    elements = [
        _make_structured_table_element(
            element_id="el_1",
            header_paths=[["Parameter"], ["Value"]],
            axis_summary={"rows": "parameter"},
        ),
        _make_structured_table_element(
            element_id="el_2",
            header_paths=[["Value"], ["Unit"]],
            axis_summary={"rows": "parameter", "columns": "unit"},
        ),
    ]

    merged = TableFragmentBuilder.merge_family_table_metadata(elements)

    assert merged["header_paths"] == [["Parameter"], ["Value"], ["Unit"]]
    assert merged["axis_summary"] == {"rows": "parameter", "columns": "unit"}
