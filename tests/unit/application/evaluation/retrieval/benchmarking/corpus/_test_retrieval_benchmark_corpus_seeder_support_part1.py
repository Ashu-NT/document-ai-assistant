from pathlib import Path

from types import SimpleNamespace

from uuid import uuid4

import pytest

from src.application.evaluation.retrieval.benchmarking.corpus import (
    RetrievalBenchmarkCorpusSeeder,
)

from src.application.evaluation.retrieval.benchmarking.corpus.retrieval_benchmark_corpus_hasher import (
    compute_hashes,
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

from src.application.workflows.ingestion import IngestionResult, IngestionStatus

from src.application.workflows.ingestion.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.reingestion_request import ReingestionRequest

from src.domain.classification import ClassificationResult, DocumentClassification

from src.domain.common import (
    ChunkType,
    DocumentType,
    ElementType,
    ModelProcessingMetadata,
    SourceLocation,
)

from src.domain.document import (
    Document,
    DocumentChunk,
    DocumentGraph,
    DocumentHashes,
    DocumentSection,
    GeneratedQuestion,
)

from src.domain.document.value_objects import DocumentStatistics

from src.domain.elements import CanonicalElement

from src.shared.exceptions import SchemaValidationError

from src.shared.execution import ActionResult

def make_workspace_temp_dir() -> Path:
    temp_dir = Path.cwd() / ".pytest_tmp_local" / uuid4().hex
    temp_dir.mkdir(parents=True, exist_ok=False)
    return temp_dir

class FakeTruthSetLoader:
    def __init__(self, dataset: RetrievalBenchmarkDataset) -> None:
        self.dataset = dataset
        self.calls: list[Path | str | None] = []

    def load(self, path: Path | str | None = None) -> RetrievalBenchmarkDataset:
        self.calls.append(path)
        return self.dataset

class FakeDuplicateDetectionService:
    def __init__(self, matches: dict[str, str] | None = None) -> None:
        self.matches = matches or {}
        self.calls: list[str] = []

    def check_file_hash(self, file_hash: str, activity_context=None) -> ActionResult:
        self.calls.append(file_hash)
        existing_document_id = self.matches.get(file_hash)
        return ActionResult(
            entity_type="document",
            entity_id=existing_document_id,
            payload={
                "is_duplicate": existing_document_id is not None,
                "existing_document_id": existing_document_id,
            },
        )

class FakeDocumentLookupService:
    def __init__(self, graphs: dict[str, DocumentGraph]) -> None:
        self.graphs = graphs
        self.calls: list[str] = []

    def get_document_graph(
        self,
        document_id: str,
        activity_context=None,
    ) -> DocumentGraph | None:
        self.calls.append(document_id)
        return self.graphs.get(document_id)

class FakeClassificationService:
    def __init__(self, classifications: dict[str, DocumentClassification]) -> None:
        self.classifications = classifications
        self.calls: list[str] = []

    def get_document_classification(
        self,
        document_id: str,
    ) -> DocumentClassification | None:
        self.calls.append(document_id)
        return self.classifications.get(document_id)

class FakeDocumentClassificationWorkflow:
    def __init__(
        self,
        operations: list[str],
        classifications_by_document_id: dict[str, DocumentClassification],
    ) -> None:
        self.operations = operations
        self.classifications_by_document_id = classifications_by_document_id
        self.calls: list[str] = []

    def classify_document(
        self,
        document_graph: DocumentGraph,
        activity_context=None,
    ) -> DocumentClassification:
        document_id = document_graph.document.document_id
        self.operations.append("classify")
        self.calls.append(document_id)
        return self.classifications_by_document_id[document_id]

class FakeIngestionWorkflow:
    def __init__(
        self,
        results_by_path: dict[str, IngestionResult] | None = None,
        reingest_results: dict[str, IngestionResult] | None = None,
        retry_extraction_results: dict[str, IngestionResult] | None = None,
        retry_extraction_errors: dict[str, Exception] | None = None,
        extraction_enabled: bool = True,
    ) -> None:
        self.results_by_path = results_by_path or {}
        self.reingest_results = reingest_results or {}
        self.retry_extraction_results = retry_extraction_results or {}
        self.retry_extraction_errors = retry_extraction_errors or {}
        self.extraction_enabled = extraction_enabled
        self.calls: list[IngestionRequest] = []
        self.reingest_calls: list[ReingestionRequest] = []
        self.retry_extraction_calls: list[str] = []

    def run(
        self,
        request: IngestionRequest,
        *,
        progress_callback=None,
        activity_context=None,
        audit_context=None,
        event_context=None,
    ) -> IngestionResult:
        self.calls.append(request)
        if progress_callback:
            progress_callback(f"fake ingestion for {request.file_path}")
        result = self.results_by_path.get(request.file_path)
        if result is None:
            raise KeyError(f"FakeIngestionWorkflow: no result configured for {request.file_path}")
        return result

    def reingest(
        self,
        request: ReingestionRequest,
        *,
        activity_context=None,
        audit_context=None,
        progress_callback=None,
    ) -> IngestionResult:
        self.reingest_calls.append(request)
        if progress_callback:
            progress_callback(f"fake reingest for {request.document_id}")
        result = self.reingest_results.get(request.document_id)
        if result is None:
            raise KeyError(
                f"FakeIngestionWorkflow: no reingest result configured for {request.document_id}"
            )
        return result

    def retry_extraction(
        self,
        document_id: str,
        *,
        activity_context=None,
        progress_callback=None,
    ) -> IngestionResult:
        self.retry_extraction_calls.append(document_id)
        if progress_callback:
            progress_callback(f"fake retry extraction for {document_id}")
        error = self.retry_extraction_errors.get(document_id)
        if error is not None:
            raise error
        result = self.retry_extraction_results.get(document_id)
        if result is None:
            raise KeyError(
                f"FakeIngestionWorkflow: no retry_extraction result configured for {document_id}"
            )
        return result

class FakeExtractionService:
    def __init__(
        self,
        documents_missing_extraction: set[str] | None = None,
        extraction_results_by_document_id: dict[str, object] | None = None,
    ) -> None:
        self.documents_missing_extraction = documents_missing_extraction or set()
        self.has_extraction_result_calls: list[str] = []
        self.get_document_extraction_result_calls: list[str] = []
        self.extraction_results_by_document_id = extraction_results_by_document_id or {}

    def has_extraction_result(self, document_id: str) -> bool:
        self.has_extraction_result_calls.append(document_id)
        return document_id not in self.documents_missing_extraction

    def get_document_extraction_result(self, document_id: str):
        self.get_document_extraction_result_calls.append(document_id)
        return self.extraction_results_by_document_id.get(document_id)

class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commit_calls = 0

    def commit(self) -> None:
        self.commit_calls += 1

def build_case(
    *,
    case_id: str,
    document_alias: str,
    file_name: str,
) -> RetrievalBenchmarkCase:
    return RetrievalBenchmarkCase(
        case_id=case_id,
        query_text=f"Question for {case_id}",
        query_type=RetrievalBenchmarkQueryType.SEMANTIC_LOOKUP,
        expected_document_alias=document_alias,
        expected_file_name=file_name,
        expected_section_path_text="Section",
        expected_page=1,
        expected_relevant_passage="Relevant passage.",
        priority=RetrievalBenchmarkPriority.HIGH,
        expected_rank_target=RetrievalBenchmarkRankTarget.TOP_3,
        notes="seed test",
    )

def build_dataset(
    source_path: Path,
    cases: list[RetrievalBenchmarkCase],
) -> RetrievalBenchmarkDataset:
    return RetrievalBenchmarkDataset(
        source_path=source_path,
        cases=cases,
    )

__all__ = [name for name in globals() if not name.startswith("__")]
