from __future__ import annotations

from collections.abc import Callable

from src.application.workflows.ingestion.content_hash import compute_content_hash_from_graph
from src.application.workflows.ingestion.stages.parsing_stage_result import (
    ParsingStageResult,
)
from src.application.workflows.parsing import ParsingWorkflow, ParsingWorkflowResult
from src.domain.common import DocumentType
from src.domain.document.value_objects import DocumentHashes
from src.shared.activity import ActivityContext


class ParsingStageRunner:
    def __init__(self, *, parsing_workflow: ParsingWorkflow) -> None:
        self.parsing_workflow = parsing_workflow

    def run(
        self,
        *,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        document_id: str | None,
        enable_ocr_override: bool | None,
        requested_title: str | None,
        requested_document_type: DocumentType | None,
        source_name: str | None,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> ParsingStageResult:
        parsing_result = self.parsing_workflow.parse(
            file_path=file_path,
            file_hash=file_hash,
            content_hash=content_hash,
            document_id=document_id,
            enable_ocr_override=enable_ocr_override,
            activity_context=activity_context,
            progress_callback=progress_callback,
        )
        self._apply_request_overrides(
            parsing_result=parsing_result,
            requested_title=requested_title,
            requested_document_type=requested_document_type,
            source_name=source_name,
        )
        resolved_content_hash = compute_content_hash_from_graph(
            parsing_result.document_graph
        )
        parsing_result.document_graph.document.hashes = DocumentHashes(
            file_hash=file_hash,
            content_hash=resolved_content_hash,
        )
        parser = getattr(self.parsing_workflow, "parser", None)
        return ParsingStageResult(
            parsing_result=parsing_result,
            content_hash=resolved_content_hash,
            parser_name=getattr(parser, "parser_name", None),
            parser_version=getattr(parser, "parser_version", None),
        )

    @staticmethod
    def _apply_request_overrides(
        *,
        parsing_result: ParsingWorkflowResult,
        requested_title: str | None,
        requested_document_type: DocumentType | None,
        source_name: str | None,
    ) -> None:
        document = parsing_result.document_graph.document
        if requested_title:
            document.title = requested_title
        if requested_document_type is not None:
            document.document_type = requested_document_type
        if source_name:
            document.source_name = source_name
