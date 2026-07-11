from __future__ import annotations

from typing import Any

from src.application.langgraph.common import resolve_answer_text, serialize_graph_value
from src.application.langgraph.common.answer_intent_resolver import resolve_answer_intent


def extract_answer(
    tool_results: dict[str, Any],
    response_text: str | None,
    *,
    reflection_decision: str | None = None,
) -> str | None:
    return resolve_answer_text(
        tool_results=tool_results,
        fallback_response_text=response_text,
        reflection_decision=reflection_decision,
    )


def extract_answer_intent(tool_results: dict[str, Any]) -> str | None:
    return resolve_answer_intent(tool_payload(tool_results, "answer_question"))


def extract_citations(tool_results: dict[str, Any]) -> list[dict[str, Any]]:
    answer_question_payload = tool_payload(tool_results, "answer_question")
    if isinstance(answer_question_payload, dict):
        citations = answer_question_payload.get("citations")
        if isinstance(citations, list):
            return serialize_graph_value(citations)

    retrieve_evidence_payload = tool_payload(tool_results, "retrieve_evidence")
    if isinstance(retrieve_evidence_payload, dict):
        citations = retrieve_evidence_payload.get("citations")
        if isinstance(citations, list):
            return serialize_graph_value(citations)

    return []


def extract_limitation_note(tool_results: dict[str, Any]) -> str | None:
    answer_question_payload = tool_payload(tool_results, "answer_question")
    if not isinstance(answer_question_payload, dict):
        return None
    value = answer_question_payload.get("limitation_note")
    return value if isinstance(value, str) and value else None


def extract_sections(tool_results: dict[str, Any]) -> list[dict[str, Any]]:
    answer_question_payload = tool_payload(tool_results, "answer_question")
    if isinstance(answer_question_payload, dict):
        sections = answer_question_payload.get("sections")
        if isinstance(sections, list):
            return serialize_graph_value(sections)
    return []


def extract_reference_notes(tool_results: dict[str, Any]) -> list[dict[str, Any]]:
    answer_question_payload = tool_payload(tool_results, "answer_question")
    if isinstance(answer_question_payload, dict):
        reference_notes = answer_question_payload.get("reference_notes")
        if isinstance(reference_notes, list):
            return serialize_graph_value(reference_notes)
    return []


def tool_payload(
    tool_results: dict[str, Any],
    tool_name: str,
) -> Any | None:
    tool_result = tool_results.get(tool_name)
    if not isinstance(tool_result, dict):
        return None
    if not tool_result.get("success", False):
        return None
    return tool_result.get("data")
