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

def test_dataset_resolver_includes_secondary_family_with_high_passage_overlap() -> None:
    benchmark_case = build_case(
        case_id="R-016",
        document_alias="report_alias",
        file_name="report.pdf",
        section_path_text="Brief Operating Instructions > 8 Commissioning > 8.2.2",
        expected_page=25,
        expected_relevant_passage=(
            "Perform position adjustment, select Pressure mode, apply LRV pressure "
            "and Get LRV, apply URV pressure and Get URV; result measuring range configured."
        ),
    )
    dataset = RetrievalBenchmarkDataset(
        source_path=Path("TestDoc/retrieval_truth_set.md"),
        cases=[benchmark_case],
    )
    manifest = build_manifest(
        build_manifest_document(
            document_alias="report_alias",
            document_id="doc_report",
            file_name="report.pdf",
        )
    )
    graph = build_graph(
        document_id="doc_report",
        file_name="report.pdf",
        chunks=[
            build_chunk(
                chunk_id="chunk_brief",
                document_id="doc_report",
                section_id="sec_brief",
                content=(
                    "8.2.2 Calibration: Perform position adjustment, select Pressure "
                    "mode, apply LRV pressure and Get LRV, apply URV pressure and Get "
                    "URV; result measuring range configured. Brief form."
                ),
                section_path=["Brief Operating Instructions", "8 Commissioning", "8.2.2"],
                page_start=25,
                page_end=25,
                sequence_number=1,
            ),
            build_chunk(
                chunk_id="chunk_full_chapter",
                document_id="doc_report",
                section_id="sec_full",
                content=(
                    "Example: Perform position adjustment, select Pressure mode, apply "
                    "LRV pressure and Get LRV, apply URV pressure and Get URV; result "
                    "measuring range configured. Full chapter with detailed prerequisites."
                ),
                section_path=["8 Commissioning", "8.2.2", "Example"],
                page_start=25,
                page_end=25,
                sequence_number=2,
            ),
        ],
    )

    resolved_dataset = RetrievalBenchmarkDatasetResolver(
        document_lookup_service=FakeDocumentLookupService({"doc_report": graph}),
    ).resolve_dataset(dataset, manifest)

    resolved_ids = resolved_dataset.cases[0].expected_chunk_ids
    assert "chunk_brief" in resolved_ids
    assert "chunk_full_chapter" in resolved_ids

def test_dataset_resolver_excludes_secondary_family_with_low_passage_overlap() -> None:
    benchmark_case = build_case(
        case_id="R-999",
        document_alias="report_alias",
        file_name="report.pdf",
        section_path_text="8 Commissioning > 8.2.1 Dry calibration",
        expected_page=24,
        expected_relevant_passage=(
            "Apply zero pressure and press Get LRV to capture the lower range value."
        ),
    )
    dataset = RetrievalBenchmarkDataset(
        source_path=Path("TestDoc/retrieval_truth_set.md"),
        cases=[benchmark_case],
    )
    manifest = build_manifest(
        build_manifest_document(
            document_alias="report_alias",
            document_id="doc_report",
            file_name="report.pdf",
        )
    )
    graph = build_graph(
        document_id="doc_report",
        file_name="report.pdf",
        chunks=[
            build_chunk(
                chunk_id="chunk_dry_cal",
                document_id="doc_report",
                section_id="sec_dry",
                content=(
                    "Apply zero pressure and press Get LRV to capture the lower range value. "
                    "Then apply full-scale pressure and press Get URV."
                ),
                section_path=["8 Commissioning", "8.2.1 Dry calibration"],
                page_start=24,
                page_end=24,
                sequence_number=1,
            ),
            build_chunk(
                chunk_id="chunk_unrelated",
                document_id="doc_report",
                section_id="sec_other",
                content=(
                    "Safety warning: Do not exceed the maximum rated pressure. "
                    "Ensure the enclosure is properly sealed before operation."
                ),
                section_path=["2 Safety", "2.1 General warnings"],
                page_start=5,
                page_end=5,
                sequence_number=2,
            ),
        ],
    )

    resolved_dataset = RetrievalBenchmarkDatasetResolver(
        document_lookup_service=FakeDocumentLookupService({"doc_report": graph}),
    ).resolve_dataset(dataset, manifest)

    resolved_ids = resolved_dataset.cases[0].expected_chunk_ids
    assert "chunk_dry_cal" in resolved_ids
    assert "chunk_unrelated" not in resolved_ids
