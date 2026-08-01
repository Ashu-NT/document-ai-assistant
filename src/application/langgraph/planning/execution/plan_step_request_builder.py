from __future__ import annotations

from typing import Any

from src.application.langgraph.nodes.node_utils import (
    attach_entity_type,
    deserialize_identifiers,
)
from src.application.langgraph.state import AgentState
from src.application.tools.documents import (
    DocumentDetailsRequest,
    FindDocumentRequest,
    ListDocumentsRequest,
)
from src.application.tools.evaluation import (
    RetrievalTraceRequest,
    RunQualityGateRequest,
)
from src.application.tools.exploration import ExploreDocumentRequest
from src.application.tools.question_answering import AnswerQuestionRequest
from src.application.tools.retrieval import RetrieveChunksRequest
from src.application.tools.retrieval.retrieve_identifiers_tool import RetrieveIdentifiersRequest
from src.application.tools.retrieval.retrieve_structured_entities_tool import (
    RetrieveStructuredEntitiesRequest,
)


def resolved_document_id(state: AgentState) -> str | None:
    return state.get("document_id") or state.get("selected_document_id")


def build_plan_step_request(
    *,
    step: Any,
    state: AgentState,
    step_outputs: dict[str, dict[str, Any]] | None = None,
):
    document_id = resolved_document_id(state)
    args = step.args
    if step.tool_name == "list_documents":
        return ListDocumentsRequest()
    if step.tool_name == "find_document":
        query_text = args.get("query_text") or state.get("document_query")
        document_selector = state.get("document_id") if not query_text else None
        return FindDocumentRequest(
            document_id=document_selector,
            query_text=query_text,
        )
    if step.tool_name == "document_details":
        return DocumentDetailsRequest(document_id=document_id)
    if step.tool_name == "explore_document":
        return ExploreDocumentRequest(document_id=document_id)
    if step.tool_name == "retrieve_chunks":
        return RetrieveChunksRequest(
            query_text=str(args.get("query_text") or state.get("question") or state["user_input"]),
            document_id=document_id,
            top_k=state.get("top_k") or 5,
        )
    if step.tool_name == "retrieve_identifiers":
        return RetrieveIdentifiersRequest(
            identifier_value=args.get("identifier_value"),
            query_text=str(args.get("query_text") or state.get("question") or state["user_input"]),
            document_id=document_id,
            top_k=state.get("top_k") or 5,
        )
    if step.tool_name == "retrieve_structured_entities":
        return RetrieveStructuredEntitiesRequest(
            entity_type=str(args.get("entity_type") or ""),
            query_text=args.get("query_text"),
            document_id=document_id,
            top_k=int(args.get("top_k") or 20),
        )
    if step.tool_name == "answer_question":
        identifier_hits = (step_outputs or {}).get("identifier_hits", {})
        structured_hits = (step_outputs or {}).get("structured_entity_hits", {})
        structured_data = structured_hits.get("data") or {}
        return AnswerQuestionRequest(
            question=str(args.get("question") or state.get("question") or state["user_input"]),
            document_id=document_id,
            top_k=state.get("top_k"),
            allow_answer_generation=state["allow_answer_generation"],
            include_context=state["include_context"],
            resolved_identifiers=deserialize_identifiers(
                (identifier_hits.get("data") or {}).get("identifiers") or []
            ),
            resolved_structured_entities=attach_entity_type(
                structured_data.get("items") or [],
                structured_data.get("entity_type"),
            ),
        )
    if step.tool_name == "run_quality_gate":
        return RunQualityGateRequest(
            report_path=args.get("report_path"),
            thresholds_path=args.get("thresholds_path"),
        )
    if step.tool_name == "retrieval_trace":
        return RetrievalTraceRequest(
            query_text=str(args.get("query_text") or state.get("question") or state["user_input"]),
            document_id=document_id,
            top_k=state.get("top_k") or 5,
            write_output=bool(args.get("write_output", True)),
        )
    raise ValueError(f"Unsupported plan tool: {step.tool_name}")
