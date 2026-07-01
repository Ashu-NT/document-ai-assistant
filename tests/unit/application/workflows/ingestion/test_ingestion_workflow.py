from __future__ import annotations

import copy
from dataclasses import replace

import pytest

from src.application.validation.ingestion import IngestionRequestValidator
from src.application.workflows.embedding import EmbeddedChunk
from src.application.workflows.ingestion import (
    IngestionRequest,
    IngestionStage,
    IngestionStatus,
    IngestionWorkflow,
    ReingestionRequest,
    ReingestionNotSupportedError,
)
from src.application.workflows.parsing import ParsingWorkflowResult
from src.domain.common import DocumentType
from src.domain.document.value_objects import DocumentStatistics
from src.shared.exceptions import DocumentParsingError
from src.shared.execution import ActionResult
from src.shared.ids import IdGenerator


class FakeIngestionRunRepository:
    def __init__(self) -> None:
        self.created = []
        self.updated = []

    def create(self, ingestion_run) -> None:
        self.created.append(copy.deepcopy(ingestion_run))

    def get(self, run_id: str):
        return None

    def update(self, ingestion_run) -> None:
        self.updated.append(copy.deepcopy(ingestion_run))

    def mark_status(self, run_id: str, status, error_message: str | None = None) -> None:
        return None


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.ingestion_runs = FakeIngestionRunRepository()
        self.commit_count = 0
        self.rollback_count = 0

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1


class FakeDuplicateDetectionService:
    def __init__(
        self,
        *,
        file_duplicate_document_id: str | None = None,
        content_duplicate_document_id: str | None = None,
    ) -> None:
        self.file_duplicate_document_id = file_duplicate_document_id
        self.content_duplicate_document_id = content_duplicate_document_id
        self.file_hash_calls = []
        self.content_hash_calls = []

    def check_file_hash(self, file_hash: str, activity_context=None) -> ActionResult:
        self.file_hash_calls.append(file_hash)
        return ActionResult(
            payload={"existing_document_id": self.file_duplicate_document_id}
        )

    def check_content_hash(
        self,
        content_hash: str,
        activity_context=None,
    ) -> ActionResult:
        self.content_hash_calls.append(content_hash)
        return ActionResult(
            payload={"existing_document_id": self.content_duplicate_document_id}
        )


class FakeParsingWorkflow:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.calls = []

    def parse(
        self,
        *,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        activity_context=None,
        progress_callback=None,
    ) -> ParsingWorkflowResult:
        self.calls.append(
            {
                "file_path": file_path,
                "file_hash": file_hash,
                "content_hash": content_hash,
            }
        )
        graph = copy.deepcopy(self.graph)
        graph.document.statistics = DocumentStatistics(
            page_count=3,
            element_count=len(graph.elements),
            section_count=len(graph.sections),
            chunk_count=len(graph.chunks),
            table_count=len(graph.tables),
            picture_count=len(graph.pictures),
            identifier_count=len(graph.identifiers),
        )
        return ParsingWorkflowResult(
            document_id=graph.document.document_id,
            file_path=file_path,
            page_count=3,
            element_count=len(graph.elements),
            section_count=len(graph.sections),
            chunk_count=len(graph.chunks),
            table_count=len(graph.tables),
            picture_count=len(graph.pictures),
            document_graph=graph,
            parse_warnings=["parser warning"],
        )


class FailingParsingWorkflow:
    def parse(
        self,
        *,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        activity_context=None,
        progress_callback=None,
    ):
        raise DocumentParsingError("Docling parse failed.")


class FakeDocumentRegistrationService:
    def __init__(self) -> None:
        self.calls = []

    def register_document_graph(self, document_graph, activity_context=None):
        self.calls.append(document_graph)
        return ActionResult(
            entity_type="document",
            entity_id=document_graph.document.document_id,
        )


class FakeDocumentClassificationWorkflow:
    def __init__(self, classification) -> None:
        self.classification = classification
        self.calls = []

    def classify_document(self, document_graph, activity_context=None):
        self.calls.append(document_graph)
        classification = copy.deepcopy(self.classification)
        classification.document_id = document_graph.document.document_id
        classification.result.document_id = document_graph.document.document_id
        classification.document_type = document_graph.document.document_type
        classification.result.predicted_label = document_graph.document.document_type.value
        return classification


class FakePostClassificationChunkFinalizationWorkflow:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.calls = []
        self.question_generation_service = type(
            "QuestionService",
            (),
            {"question_generation_model": "qgen-test"},
        )()

    def finalize(
        self,
        document_id: str,
        *,
        max_questions_per_chunk: int = 5,
        embed_final_chunks: bool = True,
        enable_question_generation: bool | None = None,
        activity_context=None,
        progress_callback=None,
    ):
        self.calls.append(
            {
                "document_id": document_id,
                "embed_final_chunks": embed_final_chunks,
                "enable_question_generation": enable_question_generation,
            }
        )
        graph = copy.deepcopy(self.graph)
        graph.document.statistics = DocumentStatistics(
            page_count=3,
            element_count=len(graph.elements),
            section_count=len(graph.sections),
            chunk_count=len(graph.chunks),
            table_count=len(graph.tables),
            picture_count=len(graph.pictures),
            identifier_count=len(graph.identifiers),
        )
        return graph


class FakeExtractionWorkflow:
    def __init__(self, extraction_result) -> None:
        self.extraction_result = extraction_result
        self.extraction_model = "extract-test"
        self.calls = []

    def extract(
        self,
        document_id: str,
        chunks,
        activity_context=None,
        progress_callback=None,
    ):
        self.calls.append(
            {
                "document_id": document_id,
                "chunks": list(chunks),
                "progress_callback": progress_callback,
            }
        )
        result = copy.deepcopy(self.extraction_result)
        result.document_id = document_id
        return result


class FakeEmbeddingWorkflow:
    def __init__(self) -> None:
        self.embedding_service = type(
            "EmbeddingService",
            (),
            {"model_name": "embed-test"},
        )()
        self.embed_calls = []
        self.store_calls = []

    def embed_chunks(self, chunks, activity_context=None, progress_callback=None):
        self.embed_calls.append(list(chunks))
        embedded = []
        for chunk in chunks:
            embedded.append(
                EmbeddedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    section_id=chunk.section_id,
                    content=chunk.content,
                    chunk_type=chunk.chunk_type,
                    section_path=list(chunk.section_path),
                    element_ids=list(chunk.element_ids),
                    table_ids=list(chunk.table_ids),
                    picture_ids=list(chunk.picture_ids),
                    source=chunk.source,
                    sequence_number=chunk.sequence_number,
                    chunk_index=chunk.chunk_index,
                    chunk_total=chunk.chunk_total,
                    embedding_text=chunk.embedding_text,
                    statistics=chunk.statistics,
                    audit=chunk.audit,
                    embedding=[0.1, 0.2, 0.3],
                )
            )
        return embedded

    def store_embedded_chunks(self, embedded_chunks, progress_callback=None):
        self.store_calls.append(list(embedded_chunks))


class FakeEventService:
    def __init__(self) -> None:
        self.events = []

    def publish(self, event, *, context=None, severity=None):
        self.events.append(event)
        return event


def _build_workflow(
    *,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
    duplicate_service: FakeDuplicateDetectionService | None = None,
    parsing_workflow=None,
    event_service=None,
):
    return IngestionWorkflow(
        unit_of_work=FakeUnitOfWork(),
        ingestion_request_validator=IngestionRequestValidator(),
        duplicate_detection_service=duplicate_service or FakeDuplicateDetectionService(),
        parsing_workflow=parsing_workflow or FakeParsingWorkflow(sample_document_graph),
        document_registration_service=FakeDocumentRegistrationService(),
        document_classification_workflow=FakeDocumentClassificationWorkflow(
            sample_document_classification
        ),
        post_classification_chunk_finalization_workflow=(
            FakePostClassificationChunkFinalizationWorkflow(sample_document_graph)
        ),
        extraction_workflow=FakeExtractionWorkflow(sample_extraction_result),
        embedding_workflow=FakeEmbeddingWorkflow(),
        id_generator=IdGenerator(),
        event_service=event_service,
    )


def test_ingestion_workflow_persists_run_and_emits_stage_events(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nmanual")
    event_service = FakeEventService()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        event_service=event_service,
    )

    result = workflow.run(
        IngestionRequest(
            file_path=str(input_file),
            document_type=DocumentType.MANUAL.value,
            generate_questions=True,
            run_quality_checks=False,
            requested_by="user_001",
        )
    )

    assert result.status == IngestionStatus.COMPLETE
    assert result.document_id == sample_document_graph.document.document_id
    assert result.vector_count == 1
    assert result.generated_question_count == len(sample_document_graph.questions)
    assert result.current_stage == IngestionStage.COMPLETE
    assert "parser warning" in result.warnings

    stored_statuses = [
        workflow.unit_of_work.ingestion_runs.created[0].status,
        *[run.status for run in workflow.unit_of_work.ingestion_runs.updated],
    ]
    assert stored_statuses == [
        IngestionStatus.PENDING,
        IngestionStatus.PARSING,
        IngestionStatus.REGISTERED,
        IngestionStatus.CLASSIFIED,
        IngestionStatus.FINALIZED,
        IngestionStatus.EXTRACTED,
        IngestionStatus.EMBEDDED,
        IngestionStatus.INDEXED,
        IngestionStatus.COMPLETE,
    ]

    assert [
        event.event_type for event in event_service.events
    ] == [
        "ingestion.started",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.stage.started",
        "ingestion.stage.completed",
        "ingestion.completed",
    ]
    assert workflow.post_classification_chunk_finalization_workflow.calls == [
        {
            "document_id": sample_document_graph.document.document_id,
            "embed_final_chunks": False,
            "enable_question_generation": True,
        }
    ]


def test_ingestion_workflow_skips_duplicate_documents(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nduplicate")
    duplicate_service = FakeDuplicateDetectionService(
        file_duplicate_document_id="doc_existing"
    )
    event_service = FakeEventService()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        duplicate_service=duplicate_service,
        event_service=event_service,
    )

    result = workflow.run(
        IngestionRequest(
            file_path=str(input_file),
            run_quality_checks=False,
        )
    )

    assert result.status == IngestionStatus.SKIPPED_FILE_DUPLICATE
    assert result.duplicate_of_document_id == "doc_existing"
    assert workflow.parsing_workflow.calls == []
    assert workflow.unit_of_work.ingestion_runs.updated[-1].status == (
        IngestionStatus.SKIPPED_FILE_DUPLICATE
    )
    assert event_service.events[-1].event_type == "ingestion.skipped_duplicate"


def test_ingestion_workflow_marks_run_failed_and_emits_failed_event(
    tmp_path,
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    input_file = tmp_path / "manual.pdf"
    input_file.write_bytes(b"%PDF-1.4\nbroken")
    event_service = FakeEventService()
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
        parsing_workflow=FailingParsingWorkflow(),
        event_service=event_service,
    )

    with pytest.raises(DocumentParsingError):
        workflow.run(
            IngestionRequest(
                file_path=str(input_file),
                run_quality_checks=False,
            )
        )

    assert workflow.unit_of_work.rollback_count == 1
    assert workflow.unit_of_work.ingestion_runs.updated[-1].status == (
        IngestionStatus.FAILED
    )
    failed_event = event_service.events[-1]
    assert failed_event.event_type == "ingestion.failed"
    assert failed_event.stage == IngestionStage.PARSING.value


def test_reingestion_is_not_supported_yet(
    sample_document_graph,
    sample_document_classification,
    sample_extraction_result,
) -> None:
    workflow = _build_workflow(
        sample_document_graph=sample_document_graph,
        sample_document_classification=sample_document_classification,
        sample_extraction_result=sample_extraction_result,
    )

    with pytest.raises(ReingestionNotSupportedError):
        workflow.reingest(ReingestionRequest(document_id="doc_001"))
