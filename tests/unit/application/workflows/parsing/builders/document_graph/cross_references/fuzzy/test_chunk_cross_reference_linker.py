from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_linker import (
    ChunkCrossReferenceLinker,
)
from src.domain.assets import TableAsset
from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.common import DocumentType, SourceLocation
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus, ChunkCrossReferenceType
from src.domain.document.entities.chunk import DocumentChunk
from src.domain.document.entities.document import Document
from src.domain.document.value_objects import DocumentHashes
from src.shared.ids import IdGenerator


def make_chunk(*, chunk_id: str, content: str, table_ids: list[str] | None = None) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content=content,
        source=SourceLocation(page_start=1, page_end=1),
        table_ids=table_ids or [],
        sequence_number=1,
    )


def make_graph(chunks: list[DocumentChunk], tables: dict[str, TableAsset]) -> DocumentGraph:
    document = Document(
        document_id="doc_001",
        file_name="manual.pdf",
        file_path="data/input/manual.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
        document_type=DocumentType.MANUAL,
    )
    graph = DocumentGraph(document=document)
    for chunk in chunks:
        graph.add_chunk(chunk)
    graph.tables = tables
    return graph


def test_link_resolves_a_table_reference_to_the_chunk_containing_that_table() -> None:
    table = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption="Table 3. Spare parts list"),
    )
    referencing_chunk = make_chunk(
        chunk_id="ref", content="Spare parts are listed in Table 3."
    )
    target_chunk = make_chunk(
        chunk_id="target", content="table contents here", table_ids=["table_1"]
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={"table_1": table})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert len(cross_references) == 1
    xref = cross_references[0]
    assert xref.reference_type == ChunkCrossReferenceType.TABLE_REFERENCE
    assert xref.source_chunk_id == "ref"
    assert xref.target_chunk_id == "target"
    assert xref.target_asset_label == "3"
    assert xref.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE


def test_link_leaves_a_table_reference_unresolved_when_no_asset_is_captioned_with_that_number() -> (
    None
):
    referencing_chunk = make_chunk(chunk_id="ref", content="See Table 9 for details.")
    graph = make_graph([referencing_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert len(cross_references) == 1
    xref = cross_references[0]
    assert xref.reference_type == ChunkCrossReferenceType.TABLE_REFERENCE
    assert xref.target_chunk_id is None
    assert xref.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED


def test_link_falls_back_to_page_proximity_when_table_has_no_caption() -> None:
    table = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption=None),
    )
    referencing_chunk = make_chunk(
        chunk_id="ref", content="Spare parts are listed in Table 3."
    )
    target_chunk = make_chunk(
        chunk_id="target", content="table contents here", table_ids=["table_1"]
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={"table_1": table})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert len(cross_references) == 1
    xref = cross_references[0]
    assert xref.target_chunk_id == "target"
    assert xref.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    assert xref.confidence_score == 0.3


def test_link_does_not_self_reference_when_the_table_reference_lands_on_its_own_chunk() -> (
    None
):
    table = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption="Table 3. Spare parts list"),
    )
    # The chunk containing the table also happens to mention "Table 3" in
    # its own text (e.g. a caption echoed into the chunk content).
    chunk = make_chunk(
        chunk_id="self",
        content="Table 3. Spare parts list",
        table_ids=["table_1"],
    )
    graph = make_graph([chunk], tables={"table_1": table})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert cross_references == []
