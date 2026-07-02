from __future__ import annotations

import inspect

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.routing import IntentRouter, RouteType
from src.application.langgraph.strategy_advisor.advisor import StrategyAdvisor
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorRequest,
    StrategyAdvisorStatus,
)
from src.application.langgraph.strategy_advisor.strategy_merge import StrategyDecisionMerger
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.langgraph.nodes.node_utils import extend_trace


class RouteRequestNode:
    def __init__(
        self,
        intent_router: IntentRouter,
        *,
        strategy_advisor: StrategyAdvisor | None = None,
        decision_merger: StrategyDecisionMerger | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.intent_router = intent_router
        self.strategy_advisor = strategy_advisor
        self.decision_merger = decision_merger or StrategyDecisionMerger()
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "route_request",
            route=state.get("route"),
        )
        decision = self._route(state)
        advisor_patch: dict[str, object] = {}
        if (
            self.strategy_advisor is not None
            and bool(state.get("llm_retrieval_strategy_enabled", False))
        ):
            decision, advisor_patch = self._apply_strategy_advisor(state, decision)
        unsafe_request_blocked = bool(
            decision.options.get("unsafe_request_blocked", False)
        )
        blocked_reason = decision.options.get("blocked_reason")
        blocked_terms = decision.options.get("blocked_terms", [])
        guardrail_decision = decision.options.get("guardrail_decision")
        guardrail_user_message = decision.options.get("guardrail_user_message")
        guardrail_trace_id = decision.options.get("guardrail_trace_id")
        guardrail_trace = decision.options.get("guardrail_trace", [])
        blocked_tools = decision.options.get("blocked_tools", [])

        clarification_message = None
        if decision.route_type in {RouteType.NEEDS_CLARIFICATION, RouteType.UNKNOWN}:
            if decision.route_type == RouteType.UNKNOWN:
                clarification_message = (
                    guardrail_user_message
                    or "Please clarify what you want me to do."
                )
            else:
                clarification_message = (
                    guardrail_user_message
                    or "Please specify the document or query more clearly."
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
                "guardrail_decision": guardrail_decision,
                "guardrail_trace_id": guardrail_trace_id,
                "blocked_tools": blocked_tools,
                "strategy_advisor_status": advisor_patch.get("strategy_advisor_status"),
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
            "guardrail_decision": guardrail_decision,
            "guardrail_user_message": guardrail_user_message,
            "guardrail_result": decision.options.get("guardrail_result"),
            "guardrail_trace_id": guardrail_trace_id,
            "guardrail_trace": list(guardrail_trace)
            if isinstance(guardrail_trace, list)
            else [],
            "blocked_tools": list(blocked_tools) if isinstance(blocked_tools, list) else [],
            "needs_clarification": decision.route_type == RouteType.NEEDS_CLARIFICATION,
            "clarification_message": clarification_message,
            "session_command": (
                decision.route_type.value if decision.is_session_command else None
            ),
            "clarification_candidate_index": decision.clarification_candidate_index,
            "trace": extend_trace(state["trace"], trace_entry),
            **advisor_patch,
        }

    def _route(self, state: AgentState):
        route_kwargs = {
            "document_id": state.get("document_id"),
            "document_query": state.get("document_query"),
        }
        signature = inspect.signature(self.intent_router.route)
        if "selected_document_id" in signature.parameters:
            route_kwargs["selected_document_id"] = state.get("selected_document_id")
        if "deep_research_enabled" in signature.parameters:
            route_kwargs["deep_research_enabled"] = bool(
                state.get("deep_research_enabled", False)
            )
        return self.intent_router.route(
            state["user_input"],
            **route_kwargs,
        )

    def _apply_strategy_advisor(
        self,
        state: AgentState,
        decision,
    ) -> tuple[object, dict[str, object]]:
        request = StrategyAdvisorRequest(
            query_text=state["user_input"],
            deterministic_route=decision.route_type.value,
            deterministic_route_confidence=decision.confidence,
            deterministic_reason=decision.reason,
            selected_document_id=state.get("selected_document_id")
            or state.get("document_id"),
            selected_document_title=state.get("selected_document_title")
            or state.get("document_title"),
            allowed_routes=_allowed_advisor_routes_for_decision(decision),
        )
        trigger_reason = self.strategy_advisor.trigger_reason(request)
        if trigger_reason is None:
            return decision, {}
        request.trigger_reason = trigger_reason
        outcome = self.strategy_advisor.advise(request)
        patch: dict[str, object] = {
            "strategy_advisor_result": serialize_graph_value(outcome.to_dict()),
            "strategy_advisor_trace": serialize_graph_value(
                {
                    "status": outcome.status.value,
                    "events": [event.to_dict() for event in outcome.events],
                    "reason": outcome.reason,
                }
            ),
            "strategy_advisor_status": outcome.status.value,
        }
        if outcome.status != StrategyAdvisorStatus.ACCEPTED or outcome.proposal is None:
            return decision, patch
        merged_decision, route_upgraded, merge_reason = self.decision_merger.merge_route_decision(
            deterministic_decision=decision,
            proposal=outcome.proposal,
            deep_research_enabled=bool(state.get("deep_research_enabled", False)),
        )
        events = list((patch["strategy_advisor_trace"] or {}).get("events", []))
        if route_upgraded:
            events.append(
                {
                    "name": "StrategyMerged",
                    "message": "Validated advisor route recommendation was merged into the deterministic route.",
                    "diagnostics": {"route": merged_decision.route_type.value},
                }
            )
        elif merge_reason:
            events.append(
                {
                    "name": "StrategyMerged",
                    "message": "Deterministic route was retained after advisor review.",
                    "diagnostics": {"reason": merge_reason},
                }
            )
        patch["strategy_advisor_trace"] = serialize_graph_value(
            {
                "status": outcome.status.value,
                "events": events,
                "reason": outcome.reason,
            }
        )
        patch["strategy_advisor_result"] = serialize_graph_value(outcome.to_dict())
        return merged_decision, patch


def _allowed_advisor_routes_for_decision(decision) -> list[str]:
    if decision.route_type in {RouteType.ANSWER_QUESTION, RouteType.DEEP_RESEARCH}:
        return [
            RouteType.ANSWER_QUESTION.value,
            RouteType.DEEP_RESEARCH.value,
        ]
    return [decision.route_type.value]
