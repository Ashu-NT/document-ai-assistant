from __future__ import annotations

import re

from src.application.langgraph.routing.route_decision import RouteDecision
from src.application.langgraph.routing.route_type import RouteType

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


class IntentRouter:
    def route(
        self,
        user_input: str,
        *,
        document_id: str | None = None,
        document_query: str | None = None,
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
