from __future__ import annotations

from src.application.workflows.retrieval.intent.retrieval_query_intent_markers import (
    CERTIFICATION_QUERY_MARKERS,
    INSTALLATION_PROCEDURE_MARKERS,
    SPECIFICATION_SETTING_MARKERS,
)
from src.application.workflows.shared.maintenance_signal_detection import (
    mentions_maintenance_interval,
)


def requests_maintenance_interval_evidence(query_text: str) -> bool:
    return mentions_maintenance_interval(query_text)


def requests_certification_evidence(query_text: str) -> bool:
    return _contains_any(query_text, CERTIFICATION_QUERY_MARKERS)


def requests_specification_setting_instructions(query_text: str) -> bool:
    return _contains_any(query_text, SPECIFICATION_SETTING_MARKERS)


def requests_installation_or_commissioning_instructions(query_text: str) -> bool:
    return _contains_any(query_text, INSTALLATION_PROCEDURE_MARKERS)


def _contains_any(query_text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in query_text for marker in markers)
