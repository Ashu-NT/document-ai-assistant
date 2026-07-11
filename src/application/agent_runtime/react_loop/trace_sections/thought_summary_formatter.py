from __future__ import annotations

from typing import Any


def format_thought_summary(route: str | None, data: dict[str, Any], user_input: str) -> str:
    intent = str((data or {}).get("answer_intent") or "")
    if route == "answer_question":
        if intent == "identifier_lookup":
            return (
                "The request asks for specific identifiers; I will retrieve and list "
                "exact values from the document."
            )
        if intent == "maintenance_summary":
            return (
                "The request is about maintenance information; I will retrieve relevant "
                "tasks, intervals, and procedures."
            )
        if intent == "procedure_steps":
            return (
                "The request asks for procedural steps; I will retrieve and present "
                "them in order."
            )
        if intent == "safety_warnings":
            return (
                "The request is about safety warnings; I will retrieve and present "
                "relevant cautions and hazards."
            )
        if intent == "troubleshooting":
            return (
                "The request asks for troubleshooting guidance; I will retrieve "
                "relevant diagnostic steps and remedies."
            )
        if intent == "specification_summary":
            return (
                "The request asks for technical specifications; I will retrieve and "
                "summarize the relevant values."
            )
        if intent == "certification_summary":
            return (
                "The request is about certifications or compliance; I will retrieve "
                "the relevant certification details."
            )
        if intent == "table_summary":
            return (
                "The request asks for tabular information; I will retrieve and present "
                "the relevant table data."
            )
        if intent == "document_summary":
            return (
                "The request asks for a document overview; I will retrieve and "
                "summarize the key sections."
            )
        return (
            "The request asks for document evidence, so I will retrieve grounded "
            "context before answering."
        )
    if route == "planned_task":
        return (
            "The request has multiple parts, so I will execute a validated plan "
            "step by step."
        )
    if route == "deep_research":
        return (
            "The request requires synthesis across multiple evidence groups; I will "
            "collect and compare task-specific evidence before writing the report."
        )
    if route == "out_of_scope":
        return (
            "This request is outside the document assistant scope, so I will not "
            "run retrieval or tools."
        )
    if route == "blocked_action" or data.get("unsafe_request_blocked"):
        if data.get("unsafe_request_blocked"):
            return (
                "The request attempts a destructive corpus operation, so I will stop "
                "before executing tools."
            )
        return (
            "The request violates a guardrail policy, so I will stop before "
            "running tools or answer generation."
        )
    if data.get("pending_clarification"):
        return "The request is ambiguous, so I need clarification before continuing."
    if route == "retrieve_evidence":
        return (
            "The request asks for supporting evidence, so I will retrieve the most "
            "relevant grounded context."
        )
    return "The request will be handled through the grounded document workflow."
