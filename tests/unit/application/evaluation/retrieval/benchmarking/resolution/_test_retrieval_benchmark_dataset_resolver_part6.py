from pathlib import Path

import pytest

from src.application.evaluation.retrieval.benchmarking.corpus.models import (
    RetrievalBenchmarkCorpusDocument,
    RetrievalBenchmarkCorpusManifest,
)

from src.application.evaluation.retrieval.benchmarking.datasets import (
    RetrievalBenchmarkDataset,
)

from src.application.evaluation.retrieval.benchmarking.enums import (
    RetrievalBenchmarkPriority,
    RetrievalBenchmarkQueryType,
    RetrievalBenchmarkRankTarget,
)

from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)

from src.application.evaluation.retrieval.benchmarking.resolution import (
    RetrievalBenchmarkDatasetResolver,
)

from src.domain.common import ChunkType, DocumentType, SourceLocation

from src.domain.document import Document, DocumentChunk, DocumentGraph, DocumentHashes

from src.domain.document.value_objects import DocumentStatistics

from src.shared.exceptions import SchemaValidationError

class FakeDocumentLookupService:
    def __init__(self, graphs: dict[str, DocumentGraph]) -> None:
        self.graphs = graphs
        self.calls: list[str] = []

    def get_document_graph(self, document_id: str, activity_context=None):
        self.calls.append(document_id)
        return self.graphs.get(document_id)

def build_case(
    *,
    case_id: str,
    document_alias: str,
    file_name: str,
    section_path_text: str,
    expected_page: int,
    expected_relevant_passage: str,
) -> RetrievalBenchmarkCase:
    return RetrievalBenchmarkCase(
        case_id=case_id,
        query_text=f"Question for {case_id}",
        query_type=RetrievalBenchmarkQueryType.SEMANTIC_LOOKUP,
        expected_document_alias=document_alias,
        expected_file_name=file_name,
        expected_section_path_text=section_path_text,
        expected_page=expected_page,
        expected_relevant_passage=expected_relevant_passage,
        priority=RetrievalBenchmarkPriority.HIGH,
        expected_rank_target=RetrievalBenchmarkRankTarget.TOP_3,
        notes="resolution test",
    )

def build_manifest(*documents: RetrievalBenchmarkCorpusDocument) -> RetrievalBenchmarkCorpusManifest:
    return RetrievalBenchmarkCorpusManifest(
        truth_set_path=Path("TestDoc/retrieval_truth_set.md"),
        input_directory=Path("TestDoc"),
        generated_at="2026-06-20T00:00:00+00:00",
        documents=list(documents),
    )

def build_manifest_document(
    *,
    document_alias: str,
    document_id: str,
    file_name: str,
) -> RetrievalBenchmarkCorpusDocument:
    return RetrievalBenchmarkCorpusDocument(
        document_alias=document_alias,
        document_id=document_id,
        file_name=file_name,
        file_path=Path("TestDoc") / file_name,
        file_hash=f"{document_id}_file_hash",
        content_hash=f"{document_id}_content_hash",
        document_type=DocumentType.MANUAL.value,
        page_count=2,
        section_count=1,
        element_count=0,
        chunk_count=1,
        question_count=0,
    )

def build_graph(
    *,
    document_id: str,
    file_name: str,
    chunks: list[DocumentChunk],
) -> DocumentGraph:
    graph = DocumentGraph(
        document=Document(
            document_id=document_id,
            file_name=file_name,
            file_path=f"TestDoc/{file_name}",
            hashes=DocumentHashes(
                file_hash=f"{document_id}_file_hash",
                content_hash=f"{document_id}_content_hash",
            ),
            title=file_name,
            document_type=DocumentType.MANUAL,
            statistics=DocumentStatistics(page_count=2),
        )
    )
    for chunk in chunks:
        graph.add_chunk(chunk)
    return graph

def build_chunk(
    *,
    chunk_id: str,
    document_id: str,
    section_id: str,
    content: str,
    section_path: list[str],
    page_start: int,
    page_end: int,
    sequence_number: int,
    chunk_index: int = 1,
    chunk_total: int = 1,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        section_id=section_id,
        content=content,
        chunk_type=ChunkType.GENERAL,
        section_path=section_path,
        source=SourceLocation(page_start=page_start, page_end=page_end),
        sequence_number=sequence_number,
        chunk_index=chunk_index,
        chunk_total=chunk_total,
    )

def test_dataset_resolver_raises_diagnostics_for_alias_file_mismatch() -> None:
    benchmark_case = build_case(
        case_id="X-001",
        document_alias="manual_alias",
        file_name="wrong.pdf",
        section_path_text="Maintenance Schedule",
        expected_page=10,
        expected_relevant_passage="Replace hydraulic filter every 1000 operating hours.",
    )
    dataset = RetrievalBenchmarkDataset(
        source_path=Path("TestDoc/retrieval_truth_set.md"),
        cases=[benchmark_case],
    )
    manifest = build_manifest(
        build_manifest_document(
            document_alias="manual_alias",
            document_id="doc_manual",
            file_name="manual.pdf",
        )
    )

    with pytest.raises(SchemaValidationError) as exc_info:
        RetrievalBenchmarkDatasetResolver(
            document_lookup_service=FakeDocumentLookupService({}),
        ).resolve_dataset(dataset, manifest)

    details = exc_info.value.details
    assert details is not None
    assert details["unresolved_case_ids"] == ["X-001"]
    assert details["diagnostics"][0]["message"] == (
        "Benchmark case alias and file name point to different seeded documents."
    )

def test_dataset_resolver_raises_specific_diagnostic_for_chunkless_graph() -> None:
    benchmark_case = build_case(
        case_id="RR-001",
        document_alias="certificate_alias",
        file_name="certificate.pdf",
        section_path_text="Certificate body > Equipment description",
        expected_page=1,
        expected_relevant_passage="ONE (1) AUXILIARY MARINE DIESEL GENERATOR.",
    )
    dataset = RetrievalBenchmarkDataset(
        source_path=Path("TestDoc/retrieval_truth_set.md"),
        cases=[benchmark_case],
    )
    manifest = build_manifest(
        build_manifest_document(
            document_alias="certificate_alias",
            document_id="doc_certificate",
            file_name="certificate.pdf",
        )
    )
    chunkless_graph = build_graph(
        document_id="doc_certificate",
        file_name="certificate.pdf",
        chunks=[],
    )

    with pytest.raises(SchemaValidationError) as exc_info:
        RetrievalBenchmarkDatasetResolver(
            document_lookup_service=FakeDocumentLookupService(
                {"doc_certificate": chunkless_graph}
            ),
        ).resolve_dataset(dataset, manifest)

    details = exc_info.value.details
    assert details is not None
    assert details["unresolved_case_ids"] == ["RR-001"]
    assert details["diagnostics"][0]["message"] == (
        "Final persisted document graph contains no chunks."
    )
    assert details["diagnostics"][0]["details"]["chunk_count"] == 0
