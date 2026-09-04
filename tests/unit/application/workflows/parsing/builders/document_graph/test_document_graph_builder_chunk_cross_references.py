from src.application.workflows.parsing import (
    ParsedCanonicalElement,
    RawParsedDocument,
)
from src.application.workflows.parsing.builders import (
    DocumentGraphBuilder,
    SectionBuilder,
)
from src.application.workflows.parsing.builders.document_graph.cross_references import (
    CrossReferenceLinkingOutcome,
)
from src.domain.common import BoundingBox, ElementType
from src.domain.document import DocumentHashes
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    CrossReferenceEvidence,
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


def make_builder(*, cross_reference_pipeline=None) -> DocumentGraphBuilder:
    id_generator = IdGenerator()
    return DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=SectionBuilder(id_generator),
        max_chunk_tokens=200,
        chunk_overlap=20,
        cross_reference_pipeline=cross_reference_pipeline,
    )


class _StubCrossReferencePipeline:
    """Test double for `CrossReferencePipeline`: returns one canned
    canonical reference and one canned evidence row per chunk in the graph,
    regardless of the chunk's real content -- fuzzy/native/reconciliation
    correctness is covered separately by their own unit tests. This test
    only verifies that `DocumentGraphBuilder.build()` calls the pipeline
    exactly once and adds both collections to the graph when (and only
    when) a pipeline is injected -- confirming mutation ownership lives
    solely in the builder, not inside the pipeline."""

    def __init__(self) -> None:
        self.run_calls: list[tuple] = []

    def run(self, graph, pdf_link_extraction_result=None):
        self.run_calls.append((graph, pdf_link_extraction_result))
        source_chunk_id = next(iter(graph.chunks))
        return CrossReferenceLinkingOutcome(
            evidence=[
                CrossReferenceEvidence(
                    evidence_id="xref_evidence_stub_1",
                    document_id=graph.document.document_id,
                    source_chunk_id=source_chunk_id,
                    reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
                    matched_text="(-> Page 42)",
                    target_page=42,
                    resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
                    confidence_score=0.0,
                )
            ],
            canonical_references=[
                ChunkCrossReference(
                    cross_reference_id="xref_stub_1",
                    document_id=graph.document.document_id,
                    source_chunk_id=source_chunk_id,
                    reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
                    matched_text="(-> Page 42)",
                    target_page=42,
                    target_chunk_id=None,
                    resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
                    confidence_score=0.0,
                )
            ],
        )


def _build_graph(*, cross_reference_pipeline=None):
    builder = make_builder(cross_reference_pipeline=cross_reference_pipeline)
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


def test_document_graph_builder_does_not_link_cross_references_when_no_pipeline_injected() -> (
    None
):
    graph = _build_graph(cross_reference_pipeline=None)

    assert graph.cross_references == {}
    assert graph.cross_reference_evidence == {}


def test_document_graph_builder_links_cross_references_when_pipeline_injected() -> None:
    pipeline = _StubCrossReferencePipeline()
    graph = _build_graph(cross_reference_pipeline=pipeline)

    assert len(pipeline.run_calls) == 1
    assert len(graph.cross_references) == 1
    cross_reference = graph.cross_references["xref_stub_1"]
    assert cross_reference.matched_text == "(-> Page 42)"
    assert cross_reference.document_id == "doc_001"

    assert len(graph.cross_reference_evidence) == 1
    evidence = graph.cross_reference_evidence["xref_evidence_stub_1"]
    assert evidence.document_id == "doc_001"


def test_document_graph_builder_records_cross_reference_count_in_statistics() -> None:
    graph = _build_graph(cross_reference_pipeline=_StubCrossReferencePipeline())

    assert graph.document.statistics.cross_reference_count == 1
