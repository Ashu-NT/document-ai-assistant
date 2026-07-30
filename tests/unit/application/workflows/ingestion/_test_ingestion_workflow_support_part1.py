from __future__ import annotations

import copy

from dataclasses import replace

from types import SimpleNamespace

import pytest

from src.application.validation.ingestion import IngestionRequestValidator

from src.application.workflows.embedding import EmbeddedChunk

from src.application.workflows.ingestion import (
    DocumentNotFoundForReingestionError,
    IngestionRequest,
    IngestionStage,
    IngestionStatus,
    IngestionWorkflow,
    ReingestionRequest,
    ReingestionNotSupportedError,
)

from src.application.workflows.parsing import ParsingWorkflowResult

from src.domain.common import ChunkType, DocumentType

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
        stale_document_id: str | None = None,
    ) -> None:
        self.file_duplicate_document_id = file_duplicate_document_id
        self.content_duplicate_document_id = content_duplicate_document_id
        self.stale_document_id = stale_document_id
        self.file_hash_calls = []
        self.content_hash_calls = []

    def check_file_hash(
        self,
        file_hash: str,
        activity_context=None,
        current_parser_version=None,
    ) -> ActionResult:
        self.file_hash_calls.append(file_hash)
        return ActionResult(
            payload={
                "existing_document_id": self.file_duplicate_document_id,
                "stale_document_id": None,
            }
        )

    def check_content_hash(
        self,
        content_hash: str,
        activity_context=None,
        current_parser_version=None,
    ) -> ActionResult:
        self.content_hash_calls.append(content_hash)
        return ActionResult(
            payload={
                "existing_document_id": self.content_duplicate_document_id,
                "stale_document_id": self.stale_document_id,
            }
        )

class FakeParsingWorkflow:
    def __init__(
        self,
        graph,
        *,
        parse_confidence: float | None = None,
        parser_version: str | None = None,
        stage_durations: dict[str, float] | None = None,
    ) -> None:
        self.graph = graph
        self.parse_confidence = parse_confidence
        self.stage_durations = stage_durations
        self.parser = SimpleNamespace(parser_version=parser_version)
        self.calls = []

    def parse(
        self,
        *,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        document_id: str | None = None,
        enable_ocr_override: bool | None = None,
        activity_context=None,
        progress_callback=None,
    ) -> ParsingWorkflowResult:
        self.calls.append(
            {
                "file_path": file_path,
                "file_hash": file_hash,
                "content_hash": content_hash,
                "document_id": document_id,
                "enable_ocr_override": enable_ocr_override,
            }
        )
        graph = copy.deepcopy(self.graph)
        if document_id is not None:
            graph.document.document_id = document_id
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
            parse_confidence=self.parse_confidence,
            stage_durations=self.stage_durations or {},
        )

class FailingParsingWorkflow:
    def __init__(self) -> None:
        self.parser = SimpleNamespace(parser_version=None)

    def parse(
        self,
        *,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        document_id: str | None = None,
        enable_ocr_override: bool | None = None,
        activity_context=None,
        progress_callback=None,
    ):
        raise DocumentParsingError("Docling parse failed.")

class FakeDocumentRegistrationService:
    def __init__(self) -> None:
        self.calls = []
        self.replace_calls = []

    def register_document_graph(self, document_graph, activity_context=None):
        self.calls.append(document_graph)
        return ActionResult(
            entity_type="document",
            entity_id=document_graph.document.document_id,
        )

    def replace_document_graph(self, document_graph, activity_context=None):
        self.replace_calls.append(document_graph)
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
    def __init__(self, extraction_result, extraction_service=None) -> None:
        self.extraction_result = extraction_result
        self.extraction_model = "extract-test"
        self.extraction_service = extraction_service
        self.calls = []

    def extract(
        self,
        document_id: str,
        chunks,
        activity_context=None,
        progress_callback=None,
        replace_existing: bool = False,
        tables=None,
        sections=None,
        base_result=None,
    ):
        self.calls.append(
            {
                "document_id": document_id,
                "chunks": list(chunks),
                "progress_callback": progress_callback,
                "replace_existing": replace_existing,
                "tables": tables,
                "sections": sections,
                "base_result": base_result,
            }
        )
        result = copy.deepcopy(self.extraction_result)
        result.document_id = document_id
        return result

__all__ = [name for name in globals() if not name.startswith("__")]
