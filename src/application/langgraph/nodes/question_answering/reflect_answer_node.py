from __future__ import annotations

from dataclasses import asdict
from typing import Any

from src.application.langgraph.common import GraphError, serialize_graph_value
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import build_error, extend_trace
from src.application.langgraph.reflection import ClarificationBuilder, ReflectionService
from src.application.langgraph.reflection.constants import (
    REFLECTION_CLARIFICATION_KIND,
    REFLECTION_SAFE_FAILURE_MESSAGE,
)
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


class ReflectAnswerNode:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        reflection_service: ReflectionService | None = None,
        clarification_builder: ClarificationBuilder | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.reflection_service = reflection_service
        self.clarification_builder = clarification_builder or ClarificationBuilder()
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "reflect_answer",
            route=state.get("route"),
        )
        if self.reflection_service is None or not state.get("reflection_enabled", False):
            trace_entry = self.recorder.finish_node(token, success=True)
            return {
                "trace": extend_trace(state["trace"], trace_entry),
            }
        if state.get("route") == RouteType.DEEP_RESEARCH.value:
            trace_entry = self.recorder.finish_node(token, success=True)
            return {
                "trace": extend_trace(state["trace"], trace_entry),
            }

        answer_payload = _tool_payload(state, "answer_question")
        if not isinstance(answer_payload, dict):
            trace_entry = self.recorder.finish_node(token, success=True)
            return {
                "trace": extend_trace(state["trace"], trace_entry),
            }

        route = answer_payload.get("route")
        if route != "retrieval_qa":
            trace_entry = self.recorder.finish_node(token, success=True)
            return {
                "trace": extend_trace(state["trace"], trace_entry),
            }

        generated_answer = (
            str(answer_payload.get("answer_text") or "").strip()
            or str(state.get("response_text") or "").strip()
        )
        retrieval_result = answer_payload.get("retrieval_result") or {}
        context_chunks = retrieval_result.get("context_chunks") or []
        approved_ids = set(answer_payload.get("approved_chunk_ids", []))
        rejected_ids = set(answer_payload.get("rejected_chunk_ids", []))
        approved_chunks = [
            chunk
            for chunk in context_chunks
            if isinstance(chunk, dict) and str(chunk.get("chunk_id") or "") in approved_ids
        ]
        rejected_chunks = [
            chunk
            for chunk in context_chunks
            if isinstance(chunk, dict) and str(chunk.get("chunk_id") or "") in rejected_ids
        ]
        if not approved_chunks and isinstance(context_chunks, list):
            approved_chunks = [chunk for chunk in context_chunks if isinstance(chunk, dict)]

        try:
            result = self.reflection_service.review(
                original_user_question=state.get("question") or state["user_input"],
                generated_answer=generated_answer,
                selected_document_id=state.get("selected_document_id")
                or state.get("document_id"),
                selected_document_title=state.get("selected_document_title")
                or state.get("document_title"),
                answer_intent=_extract_answer_intent(answer_payload),
                approved_chunks=approved_chunks,
                rejected_chunks=rejected_chunks,
                citations=answer_payload.get("citations", []),
                reflection_attempts=state.get("reflection_attempts", 0),
                retrieval_retry_count=state.get("retrieval_retry_count", 0),
            )
        except GraphError as exc:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code=exc.error_code,
                diagnostics=exc.details,
            )
            return {
                "error": build_error(
                    message=exc.message,
                    error_code=exc.error_code,
                    diagnostics=exc.details,
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        reflection_trace = list(state.get("reflection_trace", []))
        reflection_trace.append(
            {
                "decision": result.decision.decision.value,
                "confidence": result.decision.confidence,
                "overall_score": result.overall_score,
                "reason": result.decision.reason,
            }
        )
        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={"decision": result.decision.decision.value},
        )
        return {
            "reflection_attempts": int(state.get("reflection_attempts", 0)) + 1,
            "reflection_result": serialize_graph_value(asdict(result)),
            "reflection_decision": result.decision.decision.value,
            "reflection_score": result.overall_score,
            "answer_quality": result.diagnostics.get("answer_quality"),
            "evidence_quality": result.diagnostics.get("evidence_quality"),
            "reflection_trace": reflection_trace,
            "trace": extend_trace(state["trace"], trace_entry),
            **self._decision_patch(state=state, result=result),
        }

    def _decision_patch(
        self,
        *,
        state: AgentState,
        result,
    ) -> dict[str, Any]:
        decision = result.decision.decision.value
        if decision == "RETRIEVE_AGAIN":
            return {
                "retry_query": result.decision.retry_query,
            }
        if decision == "CLARIFY":
            plan = self.clarification_builder.build(
                decision=result.decision,
                original_user_input=state.get("question") or state["user_input"],
                answer_intent=state.get("tool_results", {})
                .get("answer_question", {})
                .get("data", {})
                .get("answer_intent"),
                selected_document_id=state.get("selected_document_id")
                or state.get("document_id"),
            )
            option_dicts = [
                {"label": option, "value": option}
                for option in plan.options
            ]
            clarification_message = "\n".join(
                [
                    "I need one clarification before answering:",
                    plan.question,
                    *[f"{index}. {option}" for index, option in enumerate(plan.options, start=1)],
                ]
            )
            return {
                "needs_clarification": True,
                "pending_clarification": {
                    "kind": REFLECTION_CLARIFICATION_KIND,
                    "resume_route": plan.resume_route,
                    "resume_payload": plan.resume_payload,
                    "original_user_input": plan.original_user_input,
                    "question": plan.question,
                    "options": plan.options,
                },
                "clarification_options": option_dicts,
                "clarification_question": plan.question,
                "clarification_message": clarification_message,
                "response_text": clarification_message,
            }
        if decision == "FAIL":
            return {
                "response_text": REFLECTION_SAFE_FAILURE_MESSAGE,
            }
        return {}


def _tool_payload(state: AgentState, tool_name: str) -> Any | None:
    tool_result = state.get("tool_results", {}).get(tool_name)
    if not isinstance(tool_result, dict):
        return None
    if not tool_result.get("success", False):
        return None
    return tool_result.get("data")


def _extract_answer_intent(answer_payload: dict[str, Any]) -> str | None:
    answer_intent = answer_payload.get("answer_intent")
    if isinstance(answer_intent, str) and answer_intent:
        return answer_intent
    diagnostics = answer_payload.get("diagnostics")
    if isinstance(diagnostics, dict):
        value = diagnostics.get("answer_intent")
        if isinstance(value, str) and value:
            return value
    return None
