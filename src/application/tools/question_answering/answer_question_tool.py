from __future__ import annotations

from dataclasses import dataclass

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.application.tools.documents import FindDocumentRequest, FindDocumentTool
from src.application.workflows.question_answering import (
    QuestionAnsweringRequest,
    QuestionAnsweringWorkflow,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk
from src.shared.exceptions import ApplicationError

_GENERATION_NOT_CONFIGURED_MESSAGE = "Answer generation is not configured."


@dataclass(slots=True, kw_only=True)
class AnswerQuestionRequest(ToolRequest):
    question: str | None = None
    document_id: str | None = None
    document_alias: str | None = None
    top_k: int | None = None
    allow_answer_generation: bool = False
    include_context: bool = False
    require_citations: bool = True
    trace: bool = False
    context_override_chunks: list[RetrievedChunk] | None = None
    retry_query: str | None = None


class AnswerQuestionTool:
    metadata = ToolMetadata(
        tool_name="answer_question",
        category="question_answering",
        description="Answer a question against a selected document or the corpus.",
        requires_llm=False,
        mutates_state=False,
    )

    def __init__(
        self,
        workflow: QuestionAnsweringWorkflow,
        find_document_tool: FindDocumentTool | None = None,
    ) -> None:
        self.workflow = workflow
        self.find_document_tool = find_document_tool

    def run(self, request: AnswerQuestionRequest) -> ToolResult:
        if not request.question or not request.question.strip():
            return invalid_request_result(
                "question is required.",
                metadata=self.metadata,
            )

        resolved_document_id = request.document_id
        if resolved_document_id is None and request.document_alias:
            if self.find_document_tool is None:
                return ToolResult.fail(
                    "document_alias resolution is not configured.",
                    error_code="unsupported_operation",
                    diagnostics={"document_alias": request.document_alias},
                    metadata=self.metadata,
                )

            find_result = self.find_document_tool.run(
                FindDocumentRequest(query_text=request.document_alias)
            )
            if not find_result.success:
                return ToolResult.fail(
                    find_result.message or "Document lookup failed.",
                    error_code=find_result.error_code,
                    diagnostics=find_result.diagnostics,
                    metadata=self.metadata,
                )
            resolved_document_id = find_result.data["document_id"]

        qa_request = QuestionAnsweringRequest(
            question=request.question.strip(),
            document_id=resolved_document_id,
            document_alias=request.document_alias,
            top_k=request.top_k,
            include_context=request.include_context,
            allow_answer_generation=request.allow_answer_generation,
            require_citations=request.require_citations,
            context_override_chunks=request.context_override_chunks,
            retry_query=request.retry_query,
        )

        try:
            result = self.workflow.run(qa_request)
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        if (
            request.allow_answer_generation
            and result.answer_text == _GENERATION_NOT_CONFIGURED_MESSAGE
        ):
            return ToolResult.fail(
                result.answer_text,
                error_code="generation_not_configured",
                diagnostics={"document_id": resolved_document_id},
                metadata=self.metadata,
                data=result,
            )

        diagnostics = {}
        if request.trace:
            diagnostics["trace_requested"] = True
            diagnostics["trace_supported"] = False

        return ToolResult.ok(
            data=result,
            diagnostics=diagnostics,
            metadata=self.metadata,
        )
