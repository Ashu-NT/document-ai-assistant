from __future__ import annotations

from src.application.guardrails import GuardrailContext
from src.application.guardrails.services import PostResponseGuardrailService
from src.application.langgraph.common import resolve_state_response_text
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
        guardrail_result, safe_response_text = self.post_response_guardrail_service.check(
            GuardrailContext(
                user_input=state.get("user_input") or "",
                query_text=state.get("user_input") or "",
                route=state.get("route"),
                document_id=state.get("document_id"),
                selected_document_id=state.get("selected_document_id"),
                selected_document_title=state.get("selected_document_title"),
                answer_text=response_text,
                citations=list((state.get("tool_results", {}).get("answer_question", {}) or {}).get("data", {}).get("citations", []) or []),
                evidence_chunks=list(state.get("merged_context_chunks", []) or state.get("initial_context_chunks", []) or []),
                runtime_mode="demo",
            )
        )
        trace_entry = self.recorder.finish_node(token, success=state.get("error") is None)
        return {
            "response_text": safe_response_text,
            "guardrail_result": guardrail_result.to_dict(),
            "guardrail_decision": guardrail_result.decision.value,
            "guardrail_trace_id": guardrail_result.trace_id,
            "guardrail_trace": guardrail_result.diagnostics.get("guardrail_trace", []),
            "trace": extend_trace(state["trace"], trace_entry),
        }
