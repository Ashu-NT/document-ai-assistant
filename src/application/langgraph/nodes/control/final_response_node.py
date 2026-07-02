from __future__ import annotations

from src.application.guardrails import GuardrailContext
from src.application.guardrails.services import PostResponseGuardrailService
from src.application.langgraph.common import (
    generated_answer_text_from_state,
    is_safe_failure_message,
    is_usable_reflection_decision,
    resolve_state_response_text,
)
from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.langgraph.nodes.node_utils import extend_trace


class FinalResponseNode:
    def __init__(
        self,
        *,
        memory: ConversationMemory | None = None,
        post_response_guardrail_service: PostResponseGuardrailService | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.memory = memory
        self.post_response_guardrail_service = (
            post_response_guardrail_service or PostResponseGuardrailService()
        )
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "final_response",
            route=state.get("route"),
        )
        if self.memory is not None:
            self.memory.save_session_state(
                session_id=state.get("session_id"),
                selected_document_id=state.get("selected_document_id"),
                selected_document_title=state.get("selected_document_title"),
                selected_document_file_name=state.get("selected_document_file_name"),
                pending_clarification=state.get("pending_clarification"),
                clarification_options=state.get("clarification_options"),
                clarification_question=state.get("clarification_question"),
            )
        response_text = (
            resolve_state_response_text(state)
            or state.get("response_text")
            or "Request completed."
        )
        reflection_decision = _reflection_decision(state)
        generated_answer = generated_answer_text_from_state(state)
        answer_payload = _tool_payload(state, "answer_question")
        guardrail_result, safe_response_text = self.post_response_guardrail_service.check(
            GuardrailContext(
                user_input=state.get("user_input") or "",
                query_text=state.get("user_input") or "",
                route=state.get("route"),
                document_id=state.get("document_id"),
                selected_document_id=state.get("selected_document_id"),
                selected_document_title=state.get("selected_document_title"),
                answer_text=response_text,
                citations=_extract_guardrail_citations(
                    state=state,
                    answer_payload=answer_payload,
                ),
                evidence_chunks=_extract_guardrail_evidence_chunks(
                    state=state,
                    answer_payload=answer_payload,
                ),
                runtime_mode="demo",
            )
        )
        final_response_text = safe_response_text
        final_response_warning = None
        if (
            is_usable_reflection_decision(reflection_decision)
            and is_safe_failure_message(final_response_text)
            and isinstance(generated_answer, str)
            and generated_answer.strip()
            and not is_safe_failure_message(generated_answer)
        ):
            final_response_text = generated_answer
            final_response_warning = (
                f"Recovered generated answer for {reflection_decision} after a "
                "safe-failure fallback attempted to replace it."
            )
        trace_entry = self.recorder.finish_node(
            token,
            success=state.get("error") is None,
            diagnostics=(
                {"final_response_warning": final_response_warning}
                if final_response_warning
                else {}
            ),
        )
        return {
            "response_text": final_response_text,
            "guardrail_result": guardrail_result.to_dict(),
            "guardrail_decision": guardrail_result.decision.value,
            "guardrail_trace_id": guardrail_result.trace_id,
            "guardrail_trace": guardrail_result.diagnostics.get("guardrail_trace", []),
            "final_response_warning": final_response_warning,
            "trace": extend_trace(state["trace"], trace_entry),
        }


def _extract_guardrail_citations(
    *,
    state: AgentState,
    answer_payload,
) -> list:
    if isinstance(answer_payload, dict):
        citations = answer_payload.get("citations")
        if isinstance(citations, list):
            return list(citations)
    retrieve_payload = _tool_payload(state, "retrieve_evidence")
    if isinstance(retrieve_payload, dict):
        citations = retrieve_payload.get("citations")
        if isinstance(citations, list):
            return list(citations)
    return []


def _extract_guardrail_evidence_chunks(
    *,
    state: AgentState,
    answer_payload,
) -> list:
    for key in ("merged_context_chunks", "retry_context_chunks", "initial_context_chunks"):
        value = state.get(key)
        if isinstance(value, list) and value:
            return list(value)

    if isinstance(answer_payload, dict):
        retrieval_result = answer_payload.get("retrieval_result")
        if isinstance(retrieval_result, dict):
            context_chunks = retrieval_result.get("context_chunks")
            if isinstance(context_chunks, list):
                return list(context_chunks)

    retrieve_payload = _tool_payload(state, "retrieve_evidence")
    if isinstance(retrieve_payload, dict):
        context_chunks = retrieve_payload.get("context_chunks")
        if isinstance(context_chunks, list):
            return list(context_chunks)
    return []


def _tool_payload(state: AgentState, tool_name: str):
    tool_result = state.get("tool_results", {}).get(tool_name)
    if not isinstance(tool_result, dict):
        return None
    if not tool_result.get("success", False):
        return None
    return tool_result.get("data")


def _reflection_decision(state: AgentState) -> str | None:
    value = state.get("reflection_decision")
    if isinstance(value, str) and value.strip():
        return value.strip()
    reflection_result = state.get("reflection_result")
    if isinstance(reflection_result, dict):
        decision = (reflection_result.get("decision") or {}).get("decision")
        if isinstance(decision, str) and decision.strip():
            return decision.strip()
    return None
