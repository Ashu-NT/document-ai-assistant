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
