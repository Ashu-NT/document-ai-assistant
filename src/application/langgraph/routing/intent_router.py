from __future__ import annotations

import re

from src.application.langgraph.routing.route_decision import RouteDecision
from src.application.langgraph.routing.route_type import RouteType

_WHITESPACE_RE = re.compile(r"\s+")


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

        if normalized_input in {"list documents", "list docs", "show documents", "documents"}:
            return RouteDecision(
                route_type=RouteType.LIST_DOCUMENTS,
                confidence=0.99,
                reason="Matched explicit list-documents command.",
            )

        if normalized_input in {"find document", "open document", "locate document"}:
            return RouteDecision(
                route_type=RouteType.NEEDS_CLARIFICATION,
                confidence=0.9,
                reason="Document lookup command is missing a target query.",
            )

        if normalized_input.startswith(("find document ", "open document ", "locate document ")):
            extracted_document_query = _strip_prefix(
                normalized_input,
                ("find document ", "open document ", "locate document "),
            )
            return RouteDecision(
                route_type=RouteType.FIND_DOCUMENT,
                confidence=0.96,
                reason="Matched explicit document lookup command.",
                extracted_document_query=extracted_document_query,
            )

        if normalized_input.startswith(("details ", "details for ", "show details ", "stats ", "statistics ")):
            extracted_document_query = _strip_prefix(
                normalized_input,
                ("details for ", "show details ", "details ", "statistics ", "stats "),
            )
            return RouteDecision(
                route_type=RouteType.DOCUMENT_DETAILS,
                confidence=0.94,
                reason="Matched explicit document details command.",
                extracted_document_query=extracted_document_query,
            )

        if normalized_input in {"explore", "explore document", "show sections", "sections"}:
            return RouteDecision(
                route_type=RouteType.NEEDS_CLARIFICATION,
                confidence=0.9,
                reason="Document exploration command is missing a target document.",
            )

        if normalized_input.startswith(("explore document ", "explore ", "what is in ")):
            extracted_document_query = _strip_prefix(
                normalized_input,
                ("explore document ", "explore ", "what is in "),
            )
            return RouteDecision(
                route_type=RouteType.DOCUMENT_EXPLORATION,
                confidence=0.94,
                reason="Matched explicit document exploration command.",
                extracted_document_query=extracted_document_query,
            )

        if normalized_input.startswith(("retrieve ", "show context ", "evidence ")):
            return RouteDecision(
                route_type=RouteType.RETRIEVE_EVIDENCE,
                confidence=0.93,
                reason="Matched explicit retrieval command.",
                extracted_document_query=extracted_document_query,
                extracted_question=_strip_prefix(
                    normalized_input,
                    ("retrieve ", "show context ", "evidence "),
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

        if normalized_input.startswith(("trace ", "show trace ", "retrieval trace ")):
            return RouteDecision(
                route_type=RouteType.RETRIEVAL_TRACE,
                confidence=0.94,
                reason="Matched explicit retrieval-trace command.",
                extracted_document_query=extracted_document_query,
                extracted_question=_strip_prefix(
                    normalized_input,
                    ("trace ", "show trace ", "retrieval trace "),
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
        )


def _normalize(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value.strip().lower())


def _strip_prefix(value: str, prefixes: tuple[str, ...]) -> str | None:
    for prefix in prefixes:
        if value.startswith(prefix):
            stripped = value[len(prefix) :].strip()
            return stripped or None
    return None
