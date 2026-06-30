from __future__ import annotations

import inspect

from src.application.langgraph.routing import IntentRouter, RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.langgraph.nodes.node_utils import extend_trace


class RouteRequestNode:
    def __init__(
        self,
        intent_router: IntentRouter,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.intent_router = intent_router
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "route_request",
            route=state.get("route"),
        )
        decision = self._route(state)
        unsafe_request_blocked = bool(
            decision.options.get("unsafe_request_blocked", False)
        )
        blocked_reason = decision.options.get("blocked_reason")
        blocked_terms = decision.options.get("blocked_terms", [])

        clarification_message = None
        if decision.route_type in {RouteType.NEEDS_CLARIFICATION, RouteType.UNKNOWN}:
            clarification_message = (
                "Please clarify what you want me to do."
                if decision.route_type == RouteType.UNKNOWN
                else "Please specify the document or query more clearly."
            )

        resolved_document_id = state.get("document_id")
        resolved_document_title = state.get("document_title")
        if (
            resolved_document_id is None
            and state.get("document_query") is None
            and state.get("selected_document_id") is not None
            and (
                decision.uses_current_document
                or decision.route_type
                in {
                    RouteType.ANSWER_QUESTION,
                    RouteType.DEEP_RESEARCH,
                    RouteType.RETRIEVE_EVIDENCE,
                    RouteType.RETRIEVAL_TRACE,
                }
            )
        ):
            resolved_document_id = state.get("selected_document_id")
            resolved_document_title = state.get("selected_document_title")

        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "route_type": decision.route_type.value,
                "confidence": decision.confidence,
                "reason": decision.reason,
                "requires_document": decision.requires_document,
                "uses_current_document": decision.uses_current_document,
                "is_compound": decision.is_compound,
                "requires_plan": decision.requires_plan,
                "plan_hint": decision.plan_hint,
                "unsafe_request_blocked": unsafe_request_blocked,
                "blocked_reason": blocked_reason,
                "blocked_terms": blocked_terms,
            },
        )
        return {
            "normalized_input": state["user_input"].strip(),
            "route": decision.route_type.value,
            "document_id": resolved_document_id,
            "document_title": resolved_document_title,
            "document_query": decision.extracted_document_query
            or state.get("document_query"),
            "question": decision.extracted_question or state["user_input"].strip(),
            "unsafe_request_blocked": unsafe_request_blocked,
            "blocked_reason": blocked_reason,
            "blocked_terms": list(blocked_terms) if isinstance(blocked_terms, list) else [],
            "needs_clarification": decision.route_type == RouteType.NEEDS_CLARIFICATION,
            "clarification_message": clarification_message,
            "session_command": (
                decision.route_type.value if decision.is_session_command else None
            ),
            "clarification_candidate_index": decision.clarification_candidate_index,
            "trace": extend_trace(state["trace"], trace_entry),
        }

    def _route(self, state: AgentState):
        route_kwargs = {
            "document_id": state.get("document_id"),
            "document_query": state.get("document_query"),
        }
        signature = inspect.signature(self.intent_router.route)
        if "deep_research_enabled" in signature.parameters:
            route_kwargs["deep_research_enabled"] = bool(
                state.get("deep_research_enabled", False)
            )
        return self.intent_router.route(
            state["user_input"],
            **route_kwargs,
        )
