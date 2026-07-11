from __future__ import annotations


def is_selected_document_maintenance_interval_context(
    *,
    question: str,
    answer_intent: str | None,
    selected_document_id: str | None,
    has_relevant_maintenance_evidence: bool,
) -> bool:
    if not selected_document_id or not has_relevant_maintenance_evidence:
        return False
    normalized_question = question.lower()
    normalized_intent = (answer_intent or "").lower()
    if "maintenance_summary" not in normalized_intent and "maintenance" not in normalized_question:
        return False
    return any(
        marker in normalized_question
        for marker in (
            "maintenance interval",
            "maintenance intervals",
            "service interval",
            "service intervals",
            "inspection interval",
            "inspection intervals",
            "maintenance schedule",
            "preventive maintenance",
            "how often",
            "schedule",
        )
    )
