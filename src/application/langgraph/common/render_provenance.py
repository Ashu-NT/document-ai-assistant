from __future__ import annotations


_PROVENANCE_LABELS: dict[str, str] = {
    "deterministic_identifier_renderer": "parsed identifier data",
    "deterministic_spare_parts_renderer": "parsed spare-parts table data",
    "deterministic_maintenance_schedule_renderer": "parsed maintenance schedule data",
    "deterministic_procedure_steps_renderer": "parsed procedure data",
    "deterministic_troubleshooting_renderer": "parsed troubleshooting data",
    "deterministic_fact_sheet_renderer": "parsed structured fact data",
}

_PROVENANCE_HEADINGS: dict[str, str] = {
    "parsed identifier data": "Requested Identifiers",
    "parsed spare-parts table data": "Spare Parts",
    "parsed maintenance schedule data": "Maintenance Schedule",
    "parsed procedure data": "Procedure Steps",
    "parsed troubleshooting data": "Troubleshooting",
    "parsed structured fact data": "Structured Facts",
}

_INTENT_HEADINGS: dict[str, str] = {
    "specification_summary": "Specification Summary",
    "maintenance_summary": "Maintenance Summary",
    "procedure_steps": "Procedure Steps",
    "safety_warnings": "SAFETY WARNING",
    "troubleshooting": "Troubleshooting",
    "certification_summary": "Certification Summary",
    "identifier_lookup": "Requested Identifiers",
    "table_summary": "Table Summary",
    "document_summary": "Document Summary",
}


def render_provenance_label(model_name: str | None) -> str | None:
    if not model_name:
        return None
    return _PROVENANCE_LABELS.get(model_name, "AI-generated summary")


def answer_heading(
    *,
    answer_intent: str | None,
    render_provenance: str | None,
) -> str:
    if render_provenance in _PROVENANCE_HEADINGS:
        if answer_intent == "certification_summary":
            return "Certification Facts"
        if answer_intent == "specification_summary":
            return "Specifications"
        return _PROVENANCE_HEADINGS[render_provenance]
    if answer_intent in _INTENT_HEADINGS:
        return _INTENT_HEADINGS[answer_intent]
    return "Final Answer"
