from __future__ import annotations

import re
from src.application.guardrails import GuardrailContext, GuardrailDecision
from src.application.guardrails.services import PreRouteGuardrailService
from src.application.langgraph.routing.route_decision import RouteDecision
from src.application.langgraph.routing.route_type import RouteType
from src.application.langgraph.routing.unsafe_action_detector import (
    UnsafeActionDetector,
)

_WHITESPACE_RE = re.compile(r"\s+")
_DIGIT_ONLY_RE = re.compile(r"^\d+$")
_OPTION_SELECTION_RE = re.compile(r"^(?:option|choose|select)\s+(\d+)$")

_LIST_DOCUMENTS_COMMANDS = {
    "list documents",
    "list docs",
    "show documents",
    "documents",
}
_HELP_COMMANDS = {"help", "commands", "what can you do"}
_EXIT_COMMANDS = {"exit", "quit", "q"}
_CURRENT_DOCUMENT_COMMANDS = {
    "current document",
    "what document is selected",
    "show selected document",
}
_CLEAR_DOCUMENT_COMMANDS = {
    "clear document",
    "forget document",
    "reset document",
    "unset document",
}
_SELECT_DOCUMENT_PREFIXES = (
    "open document ",
    "open ",
    "select document ",
    "select ",
    "use document ",
    "set document ",
    "switch to ",
)
_FIND_DOCUMENT_PREFIXES = ("find document ", "locate document ")
_DETAILS_PREFIXES = (
    "details for ",
    "show details ",
    "details ",
    "statistics ",
    "stats ",
)
_EXPLORATION_PREFIXES = ("explore document ", "explore ", "what is in ")
_RETRIEVAL_PREFIXES = ("retrieve ", "show context ", "evidence ")
_TRACE_PREFIXES = ("trace ", "show trace ", "retrieval trace ")
_EXPLORATION_CURRENT_COMMANDS = {
    "explore",
    "explore document",
    "explore it",
    "show sections",
    "sections",
    "what is in this document",
    "what is in it",
}
_QUESTION_CURRENT_REFERENCES = (
    " this document",
    " this manual",
    " this report",
    " this certificate",
    " this drawing",
    " this datasheet",
    " it",
)
_PLANNED_COMPARE_MARKERS = ("compare",)
_PLANNED_RETRIEVE_MARKERS = (
    "retrieve evidence",
    "show context",
    "summarize evidence",
)
_PLANNED_EXPLORE_MARKERS = ("explore",)
_PLANNED_LIST_AND_FIND_MARKERS = ("show documents", "list documents")
_PLANNED_FOLLOW_UP_MARKERS = (
    "summarize",
    "answer",
    "maintenance",
    "specification",
    "safety",
    "procedure",
    "troubleshooting",
    "tables",
)
_DEEP_RESEARCH_ROUTE_MARKERS = (
    "compare",
    "analyze",
    "research",
    "report",
    "checklist",
    "summarize all",
    "find every",
    "identify missing",
    "cross-check",
    "across the document",
    "all maintenance",
    "all inspection",
    "all warnings",
    "all specifications",
    "preventive maintenance",
    "evidence supports",
)
_DEEP_RESEARCH_COMPLEX_MARKERS = (
    "compare",
    "summarize all",
    "find every",
    "all maintenance",
    "all inspection",
    "all warnings",
    "all specifications",
    "preventive maintenance",
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
        normalized_input = _normalize(user_input)
        extracted_document_query = document_query

        clarification_candidate_index = _extract_candidate_index(normalized_input)
        if clarification_candidate_index is not None:
            return RouteDecision(
                route_type=RouteType.CLARIFICATION_RESPONSE,
                confidence=0.99,
                reason="Matched numeric clarification response.",
                clarification_candidate_index=clarification_candidate_index,
                is_session_command=True,
            )

        if normalized_input in _HELP_COMMANDS:
            return RouteDecision(
                route_type=RouteType.HELP,
                confidence=0.99,
                reason="Matched help command.",
                is_session_command=True,
            )

        if normalized_input in _EXIT_COMMANDS:
            return RouteDecision(
                route_type=RouteType.EXIT,
                confidence=0.99,
                reason="Matched exit command.",
                is_session_command=True,
            )

        if normalized_input in _CURRENT_DOCUMENT_COMMANDS:
            return RouteDecision(
                route_type=RouteType.CURRENT_DOCUMENT,
                confidence=0.99,
                reason="Matched current-document command.",
                requires_document=False,
                uses_current_document=True,
                is_session_command=True,
            )

        if normalized_input in _CLEAR_DOCUMENT_COMMANDS:
            return RouteDecision(
                route_type=RouteType.CLEAR_DOCUMENT,
                confidence=0.99,
                reason="Matched clear-document command.",
                is_session_command=True,
            )

        if normalized_input in _LIST_DOCUMENTS_COMMANDS:
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
            return self._guardrail_decision(
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

        if normalized_input.startswith(_SELECT_DOCUMENT_PREFIXES):
            extracted_document_query = _strip_prefix(
                normalized_input,
                _SELECT_DOCUMENT_PREFIXES,
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

        if normalized_input.startswith(_FIND_DOCUMENT_PREFIXES):
            extracted_document_query = _strip_prefix(
                normalized_input,
                _FIND_DOCUMENT_PREFIXES,
            )
            return RouteDecision(
                route_type=RouteType.FIND_DOCUMENT,
                confidence=0.96,
                reason="Matched explicit document lookup command.",
                extracted_document_query=extracted_document_query,
                requires_document=True,
            )

        if normalized_input.startswith(_DETAILS_PREFIXES):
            extracted_document_query = _strip_prefix(
                normalized_input,
                _DETAILS_PREFIXES,
            )
            return RouteDecision(
                route_type=RouteType.DOCUMENT_DETAILS,
                confidence=0.94,
                reason="Matched explicit document details command.",
                extracted_document_query=extracted_document_query,
                requires_document=True,
                uses_current_document=extracted_document_query is None,
            )

        if normalized_input in _EXPLORATION_CURRENT_COMMANDS:
            return RouteDecision(
                route_type=RouteType.DOCUMENT_EXPLORATION,
                confidence=0.95,
                reason="Matched current-document exploration command.",
                requires_document=True,
                uses_current_document=True,
            )

        if normalized_input.startswith(_EXPLORATION_PREFIXES):
            if _looks_like_planned_task(normalized_input):
                return _planned_task_decision(
                    user_input=user_input,
                    extracted_document_query=extracted_document_query,
                    normalized_input=normalized_input,
                )
            extracted_document_query = _strip_prefix(
                normalized_input,
                _EXPLORATION_PREFIXES,
            )
            return RouteDecision(
                route_type=RouteType.DOCUMENT_EXPLORATION,
                confidence=0.94,
                reason="Matched explicit document exploration command.",
                extracted_document_query=extracted_document_query,
                requires_document=True,
            )

        if normalized_input.startswith(_RETRIEVAL_PREFIXES):
            if _looks_like_planned_task(normalized_input):
                return _planned_task_decision(
                    user_input=user_input,
                    extracted_document_query=extracted_document_query,
                    normalized_input=normalized_input,
                )
            return RouteDecision(
                route_type=RouteType.RETRIEVE_EVIDENCE,
                confidence=0.93,
                reason="Matched explicit retrieval command.",
                extracted_document_query=extracted_document_query,
                extracted_question=_strip_prefix(
                    normalized_input,
                    _RETRIEVAL_PREFIXES,
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

        if normalized_input.startswith(_TRACE_PREFIXES):
            return RouteDecision(
                route_type=RouteType.RETRIEVAL_TRACE,
                confidence=0.94,
                reason="Matched explicit retrieval-trace command.",
                extracted_document_query=extracted_document_query,
                extracted_question=_strip_prefix(
                    normalized_input,
                    _TRACE_PREFIXES,
                ),
            )

        if _looks_like_deep_research(
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
                uses_current_document=_references_current_document(normalized_input),
                is_compound=True,
            )

        if _looks_like_planned_task(normalized_input):
            return _planned_task_decision(
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
            uses_current_document=_references_current_document(normalized_input),
        )

    @staticmethod
    def _guardrail_decision(
        *,
        result,
        user_input: str,
        extracted_document_query: str | None,
    ) -> RouteDecision:
        options = {
            "guardrail_decision": result.decision.value,
            "guardrail_reason": result.reason,
            "guardrail_user_message": result.user_message,
            "guardrail_result": result.to_dict(),
            "guardrail_trace_id": result.trace_id,
            "guardrail_trace": result.diagnostics.get("guardrail_trace", []),
            "blocked_tools": list(result.blocked_tools),
        }
        violations = result.violations
        if violations:
            first_violation = violations[0]
            options["blocked_terms"] = list(first_violation.matched_terms)
            options["blocked_severity"] = (
                first_violation.severity.value
                if first_violation.severity is not None
                else result.severity.value
            )
        if result.decision in {
            GuardrailDecision.REDIRECT,
            GuardrailDecision.OUT_OF_SCOPE,
        }:
            return RouteDecision(
                route_type=RouteType.OUT_OF_SCOPE,
                confidence=1.0,
                reason=result.reason,
                extracted_document_query=extracted_document_query,
                extracted_question=user_input.strip(),
                options=options,
            )
        if result.decision in {
            GuardrailDecision.CLARIFY,
            GuardrailDecision.NEEDS_CLARIFICATION,
        }:
            return RouteDecision(
                route_type=RouteType.NEEDS_CLARIFICATION,
                confidence=0.95,
                reason=result.reason,
                extracted_document_query=extracted_document_query,
                extracted_question=user_input.strip(),
                options=options,
            )
        options["unsafe_request_blocked"] = (
            result.diagnostics.get("scope_category")
            == "unsafe_destructive"
        )
        options["blocked_reason"] = result.reason
        return RouteDecision(
            route_type=RouteType.BLOCKED_ACTION,
            confidence=1.0,
            reason=result.reason,
            extracted_document_query=extracted_document_query,
            extracted_question=user_input.strip(),
            options=options,
        )


def _normalize(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value.strip().lower())


def _strip_prefix(value: str, prefixes: tuple[str, ...]) -> str | None:
    for prefix in prefixes:
        if value.startswith(prefix):
            stripped = value[len(prefix) :].strip()
            return stripped or None
    return None


def _extract_candidate_index(value: str) -> int | None:
    if not value:
        return None
    if _DIGIT_ONLY_RE.fullmatch(value):
        return max(int(value) - 1, 0)
    match = _OPTION_SELECTION_RE.fullmatch(value)
    if match is None:
        return None
    return max(int(match.group(1)) - 1, 0)


def _references_current_document(value: str) -> bool:
    if value in {"answer this document", "answer from this document"}:
        return True
    return any(reference in f" {value}" for reference in _QUESTION_CURRENT_REFERENCES)


def _looks_like_planned_task(value: str) -> bool:
    padded = f" {value} "
    if "compare" in value and " and " in padded:
        return True
    if any(marker in value for marker in _PLANNED_RETRIEVE_MARKERS) and " and " in padded:
        return any(marker in value for marker in _PLANNED_FOLLOW_UP_MARKERS)
    if any(marker in value for marker in _PLANNED_EXPLORE_MARKERS) and " and " in padded:
        return any(marker in value for marker in _PLANNED_FOLLOW_UP_MARKERS)
    if any(marker in value for marker in _PLANNED_LIST_AND_FIND_MARKERS) and any(
        marker in value for marker in ("open ", "find ", "open document ")
    ):
        return True
    return False


def _planned_task_decision(
    *,
    user_input: str,
    extracted_document_query: str | None,
    normalized_input: str,
    ) -> RouteDecision:
    return RouteDecision(
        route_type=RouteType.PLANNED_TASK,
        confidence=0.9,
        reason="Detected a deterministic compound request that should use the planning path.",
        extracted_document_query=extracted_document_query,
        extracted_question=user_input.strip(),
        uses_current_document=_references_current_document(normalized_input),
        is_compound=True,
        requires_plan=True,
        plan_hint=user_input.strip(),
    )


def _looks_like_deep_research(
    value: str,
    *,
    deep_research_enabled: bool,
) -> bool:
    padded = f" {value} "
    if any(marker in value for marker in _DEEP_RESEARCH_ROUTE_MARKERS if marker != "compare"):
        return True
    if "compare" in value and (" and " in padded or " with " in padded):
        return True
    if deep_research_enabled and any(marker in value for marker in _DEEP_RESEARCH_COMPLEX_MARKERS):
        return True
    return False
