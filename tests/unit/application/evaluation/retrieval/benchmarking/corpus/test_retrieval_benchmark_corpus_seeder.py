from pathlib import Path
from uuid import uuid4

import pytest

from src.application.evaluation.retrieval.benchmarking.corpus import (
    RetrievalBenchmarkCorpusSeeder,
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
        retry_extraction_results: dict[str, IngestionResult] | None = None,
    ) -> None:
        self.results_by_path = results_by_path or {}
        self.retry_extraction_results = retry_extraction_results or {}
        self.calls: list[IngestionRequest] = []
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

    def retry_extraction(self, document_id: str, *, activity_context=None) -> IngestionResult:
        self.retry_extraction_calls.append(document_id)
        result = self.retry_extraction_results.get(document_id)
        if result is None:
            raise KeyError(
                f"FakeIngestionWorkflow: no retry_extraction result configured for {document_id}"
            )
        return result


class FakeExtractionService:
    def __init__(self, documents_missing_extraction: set[str] | None = None) -> None:
        self.documents_missing_extraction = documents_missing_extraction or set()
        self.has_extraction_result_calls: list[str] = []

    def has_extraction_result(self, document_id: str) -> bool:
        self.has_extraction_result_calls.append(document_id)
        return document_id not in self.documents_missing_extraction


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


def build_document_graph(
    *,
    document_id: str,
    file_name: str,
    file_path: str,
    document_type: DocumentType,
    chunk_texts: list[str],
    question_count: int = 0,
) -> DocumentGraph:
    document = Document(
        document_id=document_id,
        file_name=file_name,
        file_path=file_path,
        hashes=DocumentHashes(
            file_hash=f"{document_id}_file_hash",
            content_hash=f"{document_id}_content_hash",
        ),
        title=file_name,
        document_type=document_type,
        statistics=DocumentStatistics(page_count=1),
    )
    graph = DocumentGraph(document=document)
    section = DocumentSection(
        section_id=f"sec_{document_id}",
        document_id=document_id,
        title="Section",
        level=1,
        section_path=["Section"],
        source=SourceLocation(page_start=1, page_end=1),
        sequence_number=1,
    )
    graph.add_section(section)

    for index, chunk_text in enumerate(chunk_texts, start=1):
        element_id = f"el_{document_id}_{index}"
        section.element_ids.append(element_id)
        graph.add_element(
            CanonicalElement(
                element_id=element_id,
                document_id=document_id,
                element_type=ElementType.TEXT,
                text=chunk_text,
                parent_section_id=section.section_id,
                reading_order=index,
                source=SourceLocation(page_start=1, page_end=1),
            )
        )
        graph.add_chunk(
            DocumentChunk(
                chunk_id=f"chunk_{document_id}_{index}",
                document_id=document_id,
                section_id=section.section_id,
                content=chunk_text,
                chunk_type=ChunkType.GENERAL,
                section_path=["Section"],
                element_ids=[element_id],
                source=SourceLocation(page_start=1, page_end=1),
                sequence_number=index,
            )
        )

    for index in range(1, question_count + 1):
        graph.questions[f"question_{document_id}_{index}"] = GeneratedQuestion(
            question_id=f"question_{document_id}_{index}",
            document_id=document_id,
            chunk_id=next(iter(graph.chunks)),
            question=f"Question {index}?",
        )

    return graph


def build_document_classification(
    *,
    document_id: str,
    document_type: DocumentType,
    confidence_score: float,
) -> DocumentClassification:
    return DocumentClassification(
        document_id=document_id,
        document_type=document_type,
        result=ClassificationResult(
            classification_id=f"classification_{document_id}",
            document_id=document_id,
            predicted_label=document_type.value,
            confidence_score=confidence_score,
            rationale="Benchmark classification.",
            evidence=["Section"],
            processing_metadata=ModelProcessingMetadata(
                model_name="qwen3:8b",
                model_type="document_classification",
                confidence=confidence_score,
            ),
        ),
    )


def build_seeder(
    *,
    dataset: RetrievalBenchmarkDataset,
    operations: list[str],
    final_graphs_by_document_id: dict[str, DocumentGraph],
    ingestion_workflow: FakeIngestionWorkflow | None = None,
    duplicate_matches: dict[str, str] | None = None,
    classifications: dict[str, DocumentClassification] | None = None,
    unit_of_work: FakeUnitOfWork | None = None,
    extraction_service: FakeExtractionService | None = None,
):
    truth_set_loader = FakeTruthSetLoader(dataset)
    classification_lookup = classifications or {}
    seeder = RetrievalBenchmarkCorpusSeeder(
        ingestion_workflow=ingestion_workflow or FakeIngestionWorkflow(),
        duplicate_detection_service=FakeDuplicateDetectionService(duplicate_matches),
        document_lookup_service=FakeDocumentLookupService(final_graphs_by_document_id),
        classification_service=FakeClassificationService(classification_lookup),
        document_classification_workflow=FakeDocumentClassificationWorkflow(
            operations,
            classification_lookup,
        ),
        truth_set_loader=truth_set_loader,
        unit_of_work=unit_of_work,
        embedding_model="test-embedding-model",
        vector_collection="test_collection",
        extraction_service=extraction_service,
    )
    return seeder, truth_set_loader


def test_seed_corpus_runs_workflows_and_builds_manifest_from_final_chunks(
) -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    first_file = input_directory / "manual.pdf"
    second_file = input_directory / "report.pdf"
    first_file.write_text("manual", encoding="utf-8")
    second_file.write_text("report", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="A-001",
                document_alias="manual_alias",
                file_name=first_file.name,
            ),
            build_case(
                case_id="A-002",
                document_alias="report_alias",
                file_name=second_file.name,
            ),
        ],
    )
    final_manual = build_document_graph(
        document_id="doc_manual",
        file_name=first_file.name,
        file_path=str(first_file),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final manual chunk 1", "final manual chunk 2"],
        question_count=2,
    )
    final_report = build_document_graph(
        document_id="doc_report",
        file_name=second_file.name,
        file_path=str(second_file),
        document_type=DocumentType.REPORT,
        chunk_texts=["final report chunk"],
        question_count=1,
    )
    classifications = {
        "doc_manual": build_document_classification(
            document_id="doc_manual",
            document_type=DocumentType.MANUAL,
            confidence_score=0.91,
        ),
        "doc_report": build_document_classification(
            document_id="doc_report",
            document_type=DocumentType.REPORT,
            confidence_score=0.84,
        ),
    }
    fake_ingestion_workflow = FakeIngestionWorkflow(
        results_by_path={
            str(first_file): IngestionResult(
                status=IngestionStatus.COMPLETE,
                document_id="doc_manual",
                file_name=first_file.name,
            ),
            str(second_file): IngestionResult(
                status=IngestionStatus.COMPLETE,
                document_id="doc_report",
                file_name=second_file.name,
            ),
        }
    )
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    seeder, truth_set_loader = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={
            "doc_manual": final_manual,
            "doc_report": final_report,
        },
        ingestion_workflow=fake_ingestion_workflow,
        classifications=classifications,
        unit_of_work=unit_of_work,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert truth_set_loader.calls == [truth_set_path]
    assert len(fake_ingestion_workflow.calls) == 2
    assert fake_ingestion_workflow.calls[0].file_path == str(first_file)
    assert fake_ingestion_workflow.calls[0].force is True
    assert fake_ingestion_workflow.calls[1].file_path == str(second_file)
    assert operations == []
    assert manifest.document_count == 2
    assert manifest.documents[0].document_alias == "manual_alias"
    assert manifest.documents[0].chunk_count == 2
    assert manifest.documents[0].question_count == 2
    assert manifest.documents[0].document_type == DocumentType.MANUAL.value
    assert manifest.documents[0].classification_confidence == 0.91
    assert manifest.documents[0].seed_status == "seeded_new"
    assert manifest.documents[1].document_alias == "report_alias"
    assert manifest.documents[1].chunk_count == 1
    assert manifest.documents[1].file_path == second_file


def test_seed_corpus_reuses_existing_duplicate_without_ingesting_again(
) -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-001",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_existing",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = RetrievalBenchmarkCorpusSeeder._compute_hashes(file_path)[0]
    classifications = {
        "doc_existing": build_document_classification(
            document_id="doc_existing",
            document_type=DocumentType.MANUAL,
            confidence_score=0.88,
        )
    }
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    fake_ingestion_workflow = FakeIngestionWorkflow()
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_existing": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        unit_of_work=unit_of_work,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert fake_ingestion_workflow.calls == []
    assert operations == []
    assert unit_of_work.commit_calls == 0
    assert manifest.documents[0].document_id == "doc_existing"
    assert manifest.documents[0].seed_status == "reused_existing"
    assert manifest.documents[0].classification_confidence == 0.88


def test_seed_corpus_reuses_existing_duplicate_when_extraction_service_confirms_it_has_extraction(
) -> None:
    """When `extraction_service` is wired, the seeder checks
    `has_extraction_result` before reusing — but a document that DOES have
    an extraction result still takes the plain reuse path, not retry."""
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-004",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_existing",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = RetrievalBenchmarkCorpusSeeder._compute_hashes(file_path)[0]
    classifications = {
        "doc_existing": build_document_classification(
            document_id="doc_existing",
            document_type=DocumentType.MANUAL,
            confidence_score=0.88,
        )
    }
    operations: list[str] = []
    fake_ingestion_workflow = FakeIngestionWorkflow()
    extraction_service = FakeExtractionService(documents_missing_extraction=set())
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_existing": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        extraction_service=extraction_service,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert extraction_service.has_extraction_result_calls == ["doc_existing"]
    assert fake_ingestion_workflow.retry_extraction_calls == []
    assert manifest.documents[0].seed_status == "reused_existing"


def test_seed_corpus_retries_extraction_for_existing_duplicate_missing_extraction(
) -> None:
    """A document that exists (chunks/classification committed) but has no
    extraction result — e.g. a prior run failed mid-batch-extraction — gets
    extraction retried in place via `IngestionWorkflow.retry_extraction`,
    not silently reused and not force-reparsed into a new document_id."""
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-005",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_existing",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = RetrievalBenchmarkCorpusSeeder._compute_hashes(file_path)[0]
    classifications = {
        "doc_existing": build_document_classification(
            document_id="doc_existing",
            document_type=DocumentType.MANUAL,
            confidence_score=0.88,
        )
    }
    operations: list[str] = []
    fake_ingestion_workflow = FakeIngestionWorkflow(
        retry_extraction_results={
            "doc_existing": IngestionResult(
                status=IngestionStatus.EXTRACTED,
                document_id="doc_existing",
                file_name=file_path.name,
            ),
        }
    )
    extraction_service = FakeExtractionService(
        documents_missing_extraction={"doc_existing"}
    )
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_existing": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        extraction_service=extraction_service,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert extraction_service.has_extraction_result_calls == ["doc_existing"]
    assert fake_ingestion_workflow.retry_extraction_calls == ["doc_existing"]
    assert fake_ingestion_workflow.calls == []
    assert manifest.documents[0].document_id == "doc_existing"
    assert manifest.documents[0].seed_status == "extraction_retried"


def test_seed_corpus_classifies_existing_duplicate_when_classification_missing(
) -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-002",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_existing",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = RetrievalBenchmarkCorpusSeeder._compute_hashes(file_path)[0]
    classification = build_document_classification(
        document_id="doc_existing",
        document_type=DocumentType.MANUAL,
        confidence_score=0.79,
    )
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_existing": final_graph},
        duplicate_matches={file_hash: "doc_existing"},
        classifications={"doc_existing": classification},
        unit_of_work=unit_of_work,
    )
    seeder.classification_service = FakeClassificationService({})

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert operations == ["classify"]
    assert unit_of_work.commit_calls == 1
    assert manifest.documents[0].seed_status == "reused_existing"
    assert manifest.documents[0].classification_confidence == 0.79


def test_seed_corpus_force_reparses_existing_duplicate_via_ingestion_workflow() -> None:
    """--force-reparse routes through the canonical IngestionWorkflow, same as a
    genuinely new document. IngestionRequest has no way to target an existing
    document_id (and reusing one would mean re-running extraction against it,
    which is unsafe today - extraction results are not replaced atomically),
    so a forced reseed always produces a *new* document_id. The old
    document_id is left in place, orphaned, since safe delete isn't supported
    yet either - that's tracked as a known, accepted limitation, not silently
    swept under the rug."""
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("duplicate", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="D-003",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_new",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final chunk"],
        question_count=1,
    )
    file_hash = RetrievalBenchmarkCorpusSeeder._compute_hashes(file_path)[0]
    classification = build_document_classification(
        document_id="doc_new",
        document_type=DocumentType.MANUAL,
        confidence_score=0.92,
    )
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    fake_ingestion_workflow = FakeIngestionWorkflow(
        results_by_path={
            str(file_path): IngestionResult(
                status=IngestionStatus.COMPLETE,
                document_id="doc_new",
                file_name=file_path.name,
            ),
        }
    )
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_new": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        duplicate_matches={file_hash: "doc_existing"},
        classifications={"doc_new": classification},
        unit_of_work=unit_of_work,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        force_reparse_existing=True,
    )

    assert len(fake_ingestion_workflow.calls) == 1
    assert fake_ingestion_workflow.calls[0].file_path == str(file_path)
    assert fake_ingestion_workflow.calls[0].force is True
    assert operations == []
    # a genuinely new document_id, distinct from the stale "doc_existing"
    assert manifest.documents[0].document_id == "doc_new"
    assert manifest.documents[0].seed_status == "reseeded_new"


def test_seed_corpus_rejects_conflicting_alias_mapping() -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    (input_directory / "first.pdf").write_text("first", encoding="utf-8")
    (input_directory / "second.pdf").write_text("second", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="C-001",
                document_alias="manual_alias",
                file_name="first.pdf",
            ),
            build_case(
                case_id="C-002",
                document_alias="manual_alias",
                file_name="second.pdf",
            ),
        ],
    )
    operations: list[str] = []
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={},
        classifications={},
    )

    with pytest.raises(SchemaValidationError):
        seeder.seed_corpus(
            truth_set_path=truth_set_path,
            input_directory=input_directory,
        )


def test_seed_corpus_fails_when_expected_file_is_missing() -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="M-001",
                document_alias="manual_alias",
                file_name="missing.pdf",
            )
        ],
    )
    operations: list[str] = []
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={},
        classifications={},
    )

    with pytest.raises(SchemaValidationError):
        seeder.seed_corpus(
            truth_set_path=truth_set_path,
            input_directory=input_directory,
        )


def test_seed_corpus_emits_progress_messages_for_major_stages() -> None:
    tmp_path = make_workspace_temp_dir()
    truth_set_path = tmp_path / "retrieval_truth_set.md"
    truth_set_path.write_text("truth set", encoding="utf-8")
    input_directory = tmp_path / "docs"
    input_directory.mkdir()
    file_path = input_directory / "manual.pdf"
    file_path.write_text("manual", encoding="utf-8")

    dataset = build_dataset(
        truth_set_path,
        [
            build_case(
                case_id="P-001",
                document_alias="manual_alias",
                file_name=file_path.name,
            )
        ],
    )
    final_graph = build_document_graph(
        document_id="doc_manual",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.MANUAL,
        chunk_texts=["final manual chunk"],
        question_count=1,
    )
    classifications = {
        "doc_manual": build_document_classification(
            document_id="doc_manual",
            document_type=DocumentType.MANUAL,
            confidence_score=0.9,
        )
    }
    fake_ingestion_workflow = FakeIngestionWorkflow(
        results_by_path={
            str(file_path): IngestionResult(
                status=IngestionStatus.COMPLETE,
                document_id="doc_manual",
                file_name=file_path.name,
            ),
        }
    )
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    seeder, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        final_graphs_by_document_id={"doc_manual": final_graph},
        ingestion_workflow=fake_ingestion_workflow,
        classifications=classifications,
        unit_of_work=unit_of_work,
    )
    messages: list[str] = []

    seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
        progress_callback=messages.append,
    )

    assert any("Loading retrieval benchmark truth set" in message for message in messages)
    assert any("Computing hashes" in message for message in messages)
    assert any("File size:" in message for message in messages)
    assert any("Delegating to canonical IngestionWorkflow" in message for message in messages)
    assert any("fake ingestion for" in message for message in messages)
    assert any("Corpus seeding completed for 1 document(s)." in message for message in messages)
