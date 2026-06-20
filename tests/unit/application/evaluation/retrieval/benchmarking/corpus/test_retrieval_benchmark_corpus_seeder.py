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
from src.application.workflows.parsing.parsing_workflow_result import (
    ParsingWorkflowResult,
)
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


class FakeDocumentRegistrationService:
    def __init__(self, operations: list[str]) -> None:
        self.operations = operations
        self.calls: list[DocumentGraph] = []

    def register_document_graph(
        self,
        document_graph: DocumentGraph,
        activity_context=None,
    ) -> ActionResult:
        self.operations.append("register")
        self.calls.append(document_graph)
        return ActionResult(
            entity_type="document",
            entity_id=document_graph.document.document_id,
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


class FakeParsingWorkflow:
    def __init__(self, operations: list[str], graphs_by_path: dict[str, DocumentGraph]) -> None:
        self.operations = operations
        self.graphs_by_path = graphs_by_path
        self.calls: list[dict[str, str | None]] = []

    def parse(
        self,
        *,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        document_id: str | None = None,
        activity_context=None,
    ) -> ParsingWorkflowResult:
        self.operations.append("parse")
        self.calls.append(
            {
                "file_path": file_path,
                "file_hash": file_hash,
                "content_hash": content_hash,
            }
        )
        graph = self.graphs_by_path[file_path]
        return ParsingWorkflowResult(
            document_id=graph.document.document_id,
            file_path=file_path,
            page_count=graph.document.statistics.page_count,
            element_count=len(graph.elements),
            section_count=len(graph.sections),
            chunk_count=len(graph.chunks),
            table_count=0,
            picture_count=0,
            document_graph=graph,
        )


class FakePostClassificationChunkFinalizationWorkflow:
    def __init__(self, operations: list[str], graphs_by_document_id: dict[str, DocumentGraph]) -> None:
        self.operations = operations
        self.graphs_by_document_id = graphs_by_document_id
        self.calls: list[str] = []

    def finalize(
        self,
        document_id: str,
        *,
        max_questions_per_chunk: int = 5,
        activity_context=None,
        progress_callback=None,
    ) -> DocumentGraph:
        self.operations.append("finalize")
        self.calls.append(document_id)
        if progress_callback is not None:
            progress_callback(f"fake finalization for {document_id}")
        return self.graphs_by_document_id[document_id]


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
    parsing_graphs_by_path: dict[str, DocumentGraph],
    final_graphs_by_document_id: dict[str, DocumentGraph],
    duplicate_matches: dict[str, str] | None = None,
    classifications: dict[str, DocumentClassification] | None = None,
    unit_of_work: FakeUnitOfWork | None = None,
):
    truth_set_loader = FakeTruthSetLoader(dataset)
    classification_lookup = classifications or {}
    parsing_workflow = FakeParsingWorkflow(operations, parsing_graphs_by_path)
    seeder = RetrievalBenchmarkCorpusSeeder(
        parsing_workflow=parsing_workflow,
        document_registration_service=FakeDocumentRegistrationService(operations),
        duplicate_detection_service=FakeDuplicateDetectionService(duplicate_matches),
        document_lookup_service=FakeDocumentLookupService(final_graphs_by_document_id),
        classification_service=FakeClassificationService(classification_lookup),
        document_classification_workflow=FakeDocumentClassificationWorkflow(
            operations,
            classification_lookup,
        ),
        post_classification_chunk_finalization_workflow=(
            FakePostClassificationChunkFinalizationWorkflow(
                operations,
                final_graphs_by_document_id,
            )
        ),
        truth_set_loader=truth_set_loader,
        unit_of_work=unit_of_work,
        embedding_model="test-embedding-model",
        vector_collection="test_collection",
    )
    return seeder, truth_set_loader, parsing_workflow


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
    provisional_manual = build_document_graph(
        document_id="doc_manual",
        file_name=first_file.name,
        file_path=str(first_file),
        document_type=DocumentType.UNKNOWN,
        chunk_texts=["provisional manual chunk"],
    )
    provisional_report = build_document_graph(
        document_id="doc_report",
        file_name=second_file.name,
        file_path=str(second_file),
        document_type=DocumentType.UNKNOWN,
        chunk_texts=["provisional report chunk"],
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
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    seeder, truth_set_loader, parsing_workflow = build_seeder(
        dataset=dataset,
        operations=operations,
        parsing_graphs_by_path={
            str(first_file): provisional_manual,
            str(second_file): provisional_report,
        },
        final_graphs_by_document_id={
            "doc_manual": final_manual,
            "doc_report": final_report,
        },
        classifications=classifications,
        unit_of_work=unit_of_work,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert truth_set_loader.calls == [truth_set_path]
    assert [call["file_path"] for call in parsing_workflow.calls] == [
        str(first_file),
        str(second_file),
    ]
    assert operations == [
        "parse",
        "register",
        "classify",
        "finalize",
        "parse",
        "register",
        "classify",
        "finalize",
    ]
    assert unit_of_work.commit_calls == 6
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


def test_seed_corpus_refinalizes_existing_duplicate_without_reparsing(
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
    seeder, _, parsing_workflow = build_seeder(
        dataset=dataset,
        operations=operations,
        parsing_graphs_by_path={},
        final_graphs_by_document_id={"doc_existing": final_graph},
        duplicate_matches={file_hash: "doc_existing"},
        classifications=classifications,
        unit_of_work=unit_of_work,
    )

    manifest = seeder.seed_corpus(
        truth_set_path=truth_set_path,
        input_directory=input_directory,
    )

    assert parsing_workflow.calls == []
    assert operations == ["finalize"]
    assert unit_of_work.commit_calls == 1
    assert manifest.documents[0].document_id == "doc_existing"
    assert manifest.documents[0].seed_status == "refinalized_existing"
    assert manifest.documents[0].classification_confidence == 0.88


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
    seeder, _, parsing_workflow = build_seeder(
        dataset=dataset,
        operations=operations,
        parsing_graphs_by_path={},
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

    assert parsing_workflow.calls == []
    assert operations == ["classify", "finalize"]
    assert unit_of_work.commit_calls == 2
    assert manifest.documents[0].classification_confidence == 0.79


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
    seeder, _, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        parsing_graphs_by_path={},
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
    seeder, _, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        parsing_graphs_by_path={},
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
    provisional_graph = build_document_graph(
        document_id="doc_manual",
        file_name=file_path.name,
        file_path=str(file_path),
        document_type=DocumentType.UNKNOWN,
        chunk_texts=["provisional manual chunk"],
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
    operations: list[str] = []
    unit_of_work = FakeUnitOfWork()
    seeder, _, _ = build_seeder(
        dataset=dataset,
        operations=operations,
        parsing_graphs_by_path={str(file_path): provisional_graph},
        final_graphs_by_document_id={"doc_manual": final_graph},
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
    assert any("Parsing document into provisional graph" in message for message in messages)
    assert any("Running document classification" in message for message in messages)
    assert any("Finalizing post-classification chunks, questions, and embeddings" in message for message in messages)
    assert any("fake finalization for doc_manual" in message for message in messages)
    assert any("Corpus seeding completed for 1 document(s)." in message for message in messages)
