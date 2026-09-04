from src.application.workflows.parsing.builders.document_graph.cross_references.cross_reference_pipeline import (
    CrossReferencePipeline,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.pdf_link_cross_reference_linker import (
    PdfLinkLinkingDiagnostics,
    PdfLinkLinkingResult,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.reconciliation.cross_reference_reconciliation_result import (
    CrossReferenceReconciliationDiagnostics,
    CrossReferenceReconciliationResult,
)
from src.domain.common import DocumentType
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities import ChunkCrossReference, ChunkCrossReferenceType
from src.domain.document.entities.document import Document
from src.domain.document.value_objects import DocumentHashes


def make_graph() -> DocumentGraph:
    return DocumentGraph(
        document=Document(
            document_id="doc_001",
            file_name="manual.pdf",
            file_path="data/input/manual.pdf",
            hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
            document_type=DocumentType.MANUAL,
        )
    )


def xref(reference_type: ChunkCrossReferenceType, source_chunk_id: str = "c1") -> ChunkCrossReference:
    return ChunkCrossReference(
        cross_reference_id="stub",
        document_id="doc_001",
        source_chunk_id=source_chunk_id,
        reference_type=reference_type,
        matched_text="matched",
    )


class FakeFuzzyLinker:
    def __init__(self, references: list[ChunkCrossReference]) -> None:
        self.references = references
        self.calls: list[DocumentGraph] = []

    def link(self, graph: DocumentGraph) -> list[ChunkCrossReference]:
        self.calls.append(graph)
        return self.references


class FakeNativeLinker:
    def __init__(self, result: PdfLinkLinkingResult) -> None:
        self.result = result
        self.calls: list[tuple] = []

    def link(self, graph, extraction_result):
        self.calls.append((graph, extraction_result))
        return self.result


class FakeReconciliationService:
    def __init__(self, result: CrossReferenceReconciliationResult) -> None:
        self.result = result
        self.calls: list[dict] = []

    def reconcile(self, *, location_type_fuzzy_references, native_result):
        self.calls.append(
            {
                "location_type_fuzzy_references": location_type_fuzzy_references,
                "native_result": native_result,
            }
        )
        return self.result


def test_table_and_figure_candidates_bypass_reconciliation_untouched() -> None:
    table_reference = xref(ChunkCrossReferenceType.TABLE_REFERENCE)
    figure_reference = xref(ChunkCrossReferenceType.FIGURE_REFERENCE)
    page_reference = xref(ChunkCrossReferenceType.PAGE_REFERENCE)
    fuzzy_linker = FakeFuzzyLinker([table_reference, figure_reference, page_reference])
    reconciliation_service = FakeReconciliationService(CrossReferenceReconciliationResult())
    pipeline = CrossReferencePipeline(
        fuzzy_linker=fuzzy_linker, reconciliation_service=reconciliation_service
    )

    outcome = pipeline.run(make_graph())

    assert table_reference in outcome.canonical_references
    assert figure_reference in outcome.canonical_references
    assert page_reference not in outcome.canonical_references
    passed_fuzzy = reconciliation_service.calls[0]["location_type_fuzzy_references"]
    assert passed_fuzzy == [page_reference]


def test_pipeline_never_mutates_graph() -> None:
    fuzzy_linker = FakeFuzzyLinker([])
    reconciliation_service = FakeReconciliationService(CrossReferenceReconciliationResult())
    pipeline = CrossReferencePipeline(
        fuzzy_linker=fuzzy_linker, reconciliation_service=reconciliation_service
    )
    graph = make_graph()

    pipeline.run(graph)

    assert graph.cross_references == {}
    assert graph.cross_reference_evidence == {}


def test_pipeline_skips_native_linker_when_extraction_result_is_none() -> None:
    fuzzy_linker = FakeFuzzyLinker([])
    native_linker = FakeNativeLinker(
        PdfLinkLinkingResult(diagnostics=PdfLinkLinkingDiagnostics())
    )
    reconciliation_service = FakeReconciliationService(CrossReferenceReconciliationResult())
    pipeline = CrossReferencePipeline(
        fuzzy_linker=fuzzy_linker,
        native_linker=native_linker,
        reconciliation_service=reconciliation_service,
    )

    pipeline.run(make_graph(), pdf_link_extraction_result=None)

    assert native_linker.calls == []
    assert reconciliation_service.calls[0]["native_result"] is None


def test_pipeline_returns_reconciliation_diagnostics_and_evidence() -> None:
    canonical = xref(ChunkCrossReferenceType.PDF_LINK_REFERENCE)
    reconciliation_result = CrossReferenceReconciliationResult(
        evidence=[],
        canonical_references=[canonical],
        diagnostics=CrossReferenceReconciliationDiagnostics(confirmed_count=1),
    )
    pipeline = CrossReferencePipeline(
        fuzzy_linker=FakeFuzzyLinker([]),
        reconciliation_service=FakeReconciliationService(reconciliation_result),
    )

    outcome = pipeline.run(make_graph())

    assert outcome.canonical_references == [canonical]
    assert outcome.reconciliation_diagnostics.confirmed_count == 1
    assert outcome.native_diagnostics is None
