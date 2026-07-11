from __future__ import annotations

from typing import Any

from src.application.agent_runtime.common.page_label_formatter import (
    format_page_range_label,
)


def build_answer_question_retrieve_payload(
    state: dict[str, Any],
) -> dict[str, Any] | None:
    chunks = _extract_answer_question_context_chunks(state)
    if not chunks:
        return None
    question = str(state.get("question") or state.get("user_input") or "").strip()
    return {
        "chunk_count": len(chunks),
        "description": _build_answer_question_retrieve_description(question),
    }


def build_answer_question_observation_payload(
    state: dict[str, Any],
) -> dict[str, Any] | None:
    chunks = _extract_answer_question_context_chunks(state)
    if not chunks:
        return None
    question = str(state.get("question") or state.get("user_input") or "").strip()
    return {
        "kind": "observation",
        "detail": _build_answer_question_observation_detail(question, chunks),
    }


def _extract_answer_question_context_chunks(state: dict[str, Any]) -> list[dict[str, Any]]:
    answer_question = ((state.get("tool_results") or {}).get("answer_question") or {})
    if not isinstance(answer_question, dict):
        return []
    if not answer_question.get("success", False):
        return []
    payload = answer_question.get("data")
    if not isinstance(payload, dict):
        return []
    retrieval_result = payload.get("retrieval_result")
    if not isinstance(retrieval_result, dict):
        return []
    context_chunks = retrieval_result.get("context_chunks")
    if not isinstance(context_chunks, list):
        return []
    approved_ids = {
        str(value)
        for value in payload.get("approved_chunk_ids", [])
        if str(value).strip()
    }
    if not approved_ids:
        return [chunk for chunk in context_chunks if isinstance(chunk, dict)]
    return [
        chunk
        for chunk in context_chunks
        if isinstance(chunk, dict)
        and str(chunk.get("chunk_id") or "").strip() in approved_ids
    ]


def _build_answer_question_retrieve_description(question: str) -> str:
    normalized = f" {question.lower()} "
    if _is_maintenance_interval_query(normalized):
        return "Searching maintenance interval evidence in selected document..."
    if "maintenance" in normalized:
        return "Searching maintenance evidence in selected document..."
    if _contains_any(normalized, ("procedure", "steps", "how to", "install", "replace")):
        return "Searching procedure evidence in selected document..."
    if _contains_any(
        normalized,
        ("specification", "technical data", "technical specification", "voltage", "power"),
    ):
        return "Searching technical specification evidence in selected document..."
    return "Searching grounded evidence in selected document..."


def _build_answer_question_observation_detail(
    question: str,
    chunks: list[dict[str, Any]],
) -> str:
    normalized = f" {question.lower()} "
    label = "grounded evidence"
    if _is_maintenance_interval_query(normalized):
        label = "maintenance interval evidence"
    elif "maintenance" in normalized:
        label = "maintenance evidence"
    elif _contains_any(normalized, ("procedure", "steps", "how to", "install", "replace")):
        label = "procedure evidence"
    elif _contains_any(
        normalized,
        ("specification", "technical data", "technical specification", "voltage", "power"),
    ):
        label = "technical specification evidence"

    pages = _collect_page_labels(chunks)
    if not pages:
        return f"Found {label}."
    if len(pages) == 1:
        return f"Found {label} on {pages[0]}."
    return f"Found {label} on {', '.join(pages)}."


def _collect_page_labels(chunks: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        source = chunk.get("source") or {}
        if not isinstance(source, dict):
            continue
        label = format_page_range_label(source)
        if not label:
            continue
        if label not in labels:
            labels.append(label)
        if len(labels) >= 3:
            break
    return labels


def _is_maintenance_interval_query(question: str) -> bool:
    return _contains_any(
        question,
        (
            "maintenance interval",
            "maintenance intervals",
            "service interval",
            "inspection interval",
            "maintenance schedule",
            "preventive maintenance",
        ),
    )


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)
