from src.application.workflows.parsing import (
    ParsedCanonicalElement,
    RawParsedDocument,
)
from src.application.workflows.parsing.builders import (
    DocumentGraphBuilder,
    SectionBuilder,
)
from src.domain.common import BoundingBox, ElementType
from src.domain.document import DocumentHashes
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
)
from src.shared.ids import IdGenerator


def make_parsed_element() -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id="txt_1",
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text="Contact Service. (-> Page 42)",
        page_start=1,
        page_end=1,
        bbox=BoundingBox(x1=1, y1=2, x2=3, y2=4),
        order_index=1,
        raw_ref="txt_1",
        metadata={},
    )


def make_raw_parsed_document() -> RawParsedDocument:
    return RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Pump Manual",
        page_count=3,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
    )


def make_builder(*, chunk_cross_reference_linker=None) -> DocumentGraphBuilder:
    id_generator = IdGenerator()
    return DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=SectionBuilder(id_generator),
        max_chunk_tokens=200,
        chunk_overlap=20,
        chunk_cross_reference_linker=chunk_cross_reference_linker,
    )


class _StubChunkCrossReferenceLinker:
    """Test double for `ChunkCrossReferenceLinker`: returns one canned
    cross-reference per chunk in the graph, regardless of the chunk's real
    content -- the linker's own detection/resolution correctness is covered
    separately by `test_chunk_cross_reference_detector.py`/
    `test_chunk_cross_reference_resolver.py`. This test only verifies that
    `DocumentGraphBuilder.build()` calls the linker and stores its output on
    `graph.cross_references` when (and only when) one is injected."""

    def link(self, graph):
        return [
            ChunkCrossReference(
                cross_reference_id="xref_stub_1",
                document_id=graph.document.document_id,
                source_chunk_id=next(iter(graph.chunks)),
                reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
                matched_text="(-> Page 42)",
                target_page=42,
                target_chunk_id=None,
                resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
                confidence_score=0.0,
            )
        ]


def _build_graph(*, chunk_cross_reference_linker=None):
    builder = make_builder(chunk_cross_reference_linker=chunk_cross_reference_linker)
    return builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[make_parsed_element()],
        raw_parsed_document=make_raw_parsed_document(),
    )


def test_document_graph_builder_does_not_link_cross_references_when_no_linker_injected() -> (
    None
):
    graph = _build_graph(chunk_cross_reference_linker=None)

    assert graph.cross_references == {}


def test_document_graph_builder_links_cross_references_when_linker_injected() -> None:
    graph = _build_graph(chunk_cross_reference_linker=_StubChunkCrossReferenceLinker())

    assert len(graph.cross_references) == 1
    cross_reference = graph.cross_references["xref_stub_1"]
    assert cross_reference.matched_text == "(-> Page 42)"
    assert cross_reference.document_id == "doc_001"


def test_document_graph_builder_records_cross_reference_count_in_statistics() -> None:
    graph = _build_graph(chunk_cross_reference_linker=_StubChunkCrossReferenceLinker())

    assert graph.document.statistics.cross_reference_count == 1
