from tests.unit.application.workflows.parsing.builders._test_document_graph_builder_part1 import (
    make_builder,
    make_parsed_element,
    make_raw_parsed_document,
)

from src.domain.common import ElementType
from src.domain.document import DocumentHashes


def test_document_graph_builder_persists_outline_and_artifact_metadata() -> None:
    builder = make_builder()
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="7 Components",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="7.1 Macerators",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Macerator body text.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    metadata = graph.document.metadata
    assert metadata["parser"] == {"name": "docling", "version": "1.2.3"}
    assert metadata["artifact_versions"]["section_path_schema"] == "3"
    assert metadata["artifact_versions"]["table_structure_schema"] == "2"
    assert metadata["outline"]["header_numberings"] == {
        "hdr_1": "7",
        "hdr_2": "7.1",
    }
    assert metadata["table_understanding"]["logical_table_family_count"] == 0
