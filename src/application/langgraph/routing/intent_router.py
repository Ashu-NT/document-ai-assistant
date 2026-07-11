from __future__ import annotations

from src.application.guardrails import GuardrailContext
from src.application.guardrails.services import PreRouteGuardrailService
from src.application.langgraph.routing.constants.route_command_patterns import (
    CLEAR_DOCUMENT_COMMANDS,
    CURRENT_DOCUMENT_COMMANDS,
    DETAILS_PREFIXES,
    EXIT_COMMANDS,
    EXPLORATION_CURRENT_COMMANDS,
    EXPLORATION_PREFIXES,
    FIND_DOCUMENT_PREFIXES,
    HELP_COMMANDS,
    LIST_DOCUMENTS_COMMANDS,
    RETRIEVAL_PREFIXES,
    SELECT_DOCUMENT_PREFIXES,
    TRACE_PREFIXES,
)
from src.application.langgraph.routing.detectors.deep_research_detector import (
    looks_like_deep_research,
)
from src.application.langgraph.routing.detectors.planned_task_detector import (
    build_planned_task_decision,
    looks_like_planned_task,
)
from src.application.langgraph.routing.pre_route_guardrail_decision_mapper import (
    map_guardrail_decision,
)
from src.application.langgraph.routing.route_decision import RouteDecision
from src.application.langgraph.routing.route_input_normalizer import (
    extract_candidate_index,
    normalize_route_input,
    references_current_document,
    strip_prefix,
)
from src.application.langgraph.routing.route_type import RouteType
from src.application.langgraph.routing.unsafe_action_detector import (
    UnsafeActionDetector,
)


class IntentRouter:
    def __init__(
        self,
        unsafe_action_detector: UnsafeActionDetector | None = None,
        pre_route_guardrail_service: PreRouteGuardrailService | None = None,
    ) -> None:
        self.unsafe_action_detector = unsafe_action_detector or UnsafeActionDetector()
        self.pre_route_guardrail_service = (
            pre_route_guardrail_service
            or PreRouteGuardrailService(
                unsafe_action_detector=self.unsafe_action_detector,
            )
        )

    def route(
        self,
        user_input: str,
        *,
        document_id: str | None = None,
        document_query: str | None = None,
        selected_document_id: str | None = None,
        deep_research_enabled: bool = False,
    ) -> RouteDecision:
        normalized_input = normalize_route_input(user_input)
        extracted_document_query = document_query

        clarification_candidate_index = extract_candidate_index(normalized_input)
        if clarification_candidate_index is not None:
            return RouteDecision(
                route_type=RouteType.CLARIFICATION_RESPONSE,
                confidence=0.99,
                reason="Matched numeric clarification response.",
                clarification_candidate_index=clarification_candidate_index,
                is_session_command=True,
            )

        if normalized_input in HELP_COMMANDS:
            return RouteDecision(
                route_type=RouteType.HELP,
                confidence=0.99,
                reason="Matched help command.",
                is_session_command=True,
            )

        if normalized_input in EXIT_COMMANDS:
            return RouteDecision(
                route_type=RouteType.EXIT,
                confidence=0.99,
                reason="Matched exit command.",
                is_session_command=True,
            )

        if normalized_input in CURRENT_DOCUMENT_COMMANDS:
            return RouteDecision(
                route_type=RouteType.CURRENT_DOCUMENT,
                confidence=0.99,
                reason="Matched current-document command.",
                requires_document=False,
                uses_current_document=True,
                is_session_command=True,
            )

        if normalized_input in CLEAR_DOCUMENT_COMMANDS:
            return RouteDecision(
                route_type=RouteType.CLEAR_DOCUMENT,
                confidence=0.99,
                reason="Matched clear-document command.",
                is_session_command=True,
            )

        if normalized_input in LIST_DOCUMENTS_COMMANDS:
            return RouteDecision(
                route_type=RouteType.LIST_DOCUMENTS,
                confidence=0.99,
                reason="Matched explicit list-documents command.",
            )

        pre_route_result = self.pre_route_guardrail_service.check(
            GuardrailContext(
                user_input=user_input,
                query_text=user_input,
                document_id=document_id,
                selected_document_id=selected_document_id or document_id,
            )
        )
        if not pre_route_result.allowed:
            return map_guardrail_decision(
                result=pre_route_result,
                user_input=user_input,
                extracted_document_query=extracted_document_query,
            )

        if normalized_input in {
            "open",
            "open document",
            "select",
            "select document",
            "use document",
            "set document",
            "switch to",
        }:
            return RouteDecision(
                route_type=RouteType.NEEDS_CLARIFICATION,
                confidence=0.9,
                reason="Document selection command is missing a target query.",
                requires_document=True,
            )

        if normalized_input.startswith(SELECT_DOCUMENT_PREFIXES):
            extracted_document_query = strip_prefix(
                normalized_input,
                SELECT_DOCUMENT_PREFIXES,
            )
            return RouteDecision(
                route_type=RouteType.SELECT_DOCUMENT,
                confidence=0.96,
                reason="Matched explicit document selection command.",
                extracted_document_query=extracted_document_query,
                requires_document=True,
            )

        if normalized_input in {"find document", "locate document"}:
            return RouteDecision(
                route_type=RouteType.NEEDS_CLARIFICATION,
                confidence=0.9,
                reason="Document lookup command is missing a target query.",
                requires_document=True,
            )

        if normalized_input.startswith(FIND_DOCUMENT_PREFIXES):
            extracted_document_query = strip_prefix(
                normalized_input,
                FIND_DOCUMENT_PREFIXES,
            )
            return RouteDecision(
                route_type=RouteType.FIND_DOCUMENT,
                confidence=0.96,
                reason="Matched explicit document lookup command.",
                extracted_document_query=extracted_document_query,
                requires_document=True,
            )

        if normalized_input.startswith(DETAILS_PREFIXES):
            extracted_document_query = strip_prefix(
                normalized_input,
                DETAILS_PREFIXES,
            )
            return RouteDecision(
                route_type=RouteType.DOCUMENT_DETAILS,
                confidence=0.94,
                reason="Matched explicit document details command.",
                extracted_document_query=extracted_document_query,
                requires_document=True,
                uses_current_document=extracted_document_query is None,
            )

        if normalized_input in EXPLORATION_CURRENT_COMMANDS:
            return RouteDecision(
                route_type=RouteType.DOCUMENT_EXPLORATION,
                confidence=0.95,
                reason="Matched current-document exploration command.",
                requires_document=True,
                uses_current_document=True,
            )

        if normalized_input.startswith(EXPLORATION_PREFIXES):
            if looks_like_planned_task(normalized_input):
                return build_planned_task_decision(
                    user_input=user_input,
                    extracted_document_query=extracted_document_query,
                    normalized_input=normalized_input,
                )
            extracted_document_query = strip_prefix(
                normalized_input,
                EXPLORATION_PREFIXES,
            )
            return RouteDecision(
                route_type=RouteType.DOCUMENT_EXPLORATION,
                confidence=0.94,
                reason="Matched explicit document exploration command.",
                extracted_document_query=extracted_document_query,
                requires_document=True,
            )

        if normalized_input.startswith(RETRIEVAL_PREFIXES):
            if looks_like_planned_task(normalized_input):
                return build_planned_task_decision(
                    user_input=user_input,
                    extracted_document_query=extracted_document_query,
                    normalized_input=normalized_input,
                )
            return RouteDecision(
                route_type=RouteType.RETRIEVE_EVIDENCE,
                confidence=0.93,
                reason="Matched explicit retrieval command.",
                extracted_document_query=extracted_document_query,
                extracted_question=strip_prefix(
                    normalized_input,
                    RETRIEVAL_PREFIXES,
                ),
            )

        if normalized_input in {"quality gate", "run quality gate"}:
            return RouteDecision(
                route_type=RouteType.QUALITY_GATE,
                confidence=0.98,
                reason="Matched explicit quality-gate command.",
            )

        if normalized_input in {"trace", "show trace", "retrieval trace"}:
            return RouteDecision(
                route_type=RouteType.NEEDS_CLARIFICATION,
                confidence=0.9,
                reason="Retrieval trace command is missing a query.",
            )

        if normalized_input.startswith(TRACE_PREFIXES):
            return RouteDecision(
                route_type=RouteType.RETRIEVAL_TRACE,
                confidence=0.94,
                reason="Matched explicit retrieval-trace command.",
                extracted_document_query=extracted_document_query,
                extracted_question=strip_prefix(
                    normalized_input,
                    TRACE_PREFIXES,
                ),
            )

        if looks_like_deep_research(
            normalized_input,
            deep_research_enabled=deep_research_enabled,
        ):
            return RouteDecision(
                route_type=RouteType.DEEP_RESEARCH,
                confidence=0.92 if deep_research_enabled else 0.88,
                reason="Detected a document research request that needs multi-hop evidence collection and synthesis.",
                extracted_document_query=extracted_document_query,
                extracted_question=user_input.strip(),
                requires_document=True,
                uses_current_document=references_current_document(normalized_input),
                is_compound=True,
            )

        if looks_like_planned_task(normalized_input):
            return build_planned_task_decision(
                user_input=user_input,
                extracted_document_query=extracted_document_query,
                normalized_input=normalized_input,
            )

        if not normalized_input and not document_id:
            return RouteDecision(
                route_type=RouteType.UNKNOWN,
                confidence=0.0,
                reason="Input was empty after normalization.",
            )

        return RouteDecision(
            route_type=RouteType.ANSWER_QUESTION,
            confidence=0.7,
            reason="Fell back to question answering.",
            extracted_document_query=extracted_document_query,
            extracted_question=user_input.strip(),
            uses_current_document=references_current_document(normalized_input),
        )
