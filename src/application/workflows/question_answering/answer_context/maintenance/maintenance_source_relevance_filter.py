from __future__ import annotations

import re

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
)
from src.application.workflows.shared.maintenance_signal_detection import (
    mentions_maintenance_interval,
)

_ACTION_PATTERN = re.compile(
    r"\b(?:clean|inspect|replace|check|lubricate|grease|drain|flush|tighten|service)\b",
    re.IGNORECASE,
)
_INTERVAL_PATTERN = re.compile(
    r"\b("
    r"every\s+\d+\s+(?:operating\s+)?hours?"
    r"|every\s+\d+\s+(?:day|days|week|weeks|month|months|year|years)"
    r"|daily|weekly|monthly|quarterly|annually|yearly"
    r"|when\s+necessary|as\s+needed"
    r")\b",
    re.IGNORECASE,
)
_MAINTENANCE_MARKERS = (
    "maintenance",
    "preventive maintenance",
    "service schedule",
    "service interval",
    "inspection schedule",
    "inspection interval",
    "lubrication",
    "commissioning",
    "shutdown",
)
_HIGH_SIGNAL_CHUNK_TYPES = frozenset(
    {
        "maintenance_interval",
        "maintenance_procedure",
    }
)
_LOW_SIGNAL_CHUNK_TYPES = frozenset(
    {
        "technical_specification",
        "certification_info",
        "overview",
        "operation_instruction",
        "troubleshooting",
        "general",
        "unknown",
    }
)
_MAINTENANCE_TABLE_KINDS = frozenset(
    {
        "maintenance_schedule_matrix",
        "maintenance_schedule_table",
    }
)


class MaintenanceSourceRelevanceFilter:
    def is_relevant(
        self,
        source: AnswerSource,
        *,
        table: AnswerTable | None,
    ) -> bool:
        if table is not None and table.table_kind in _MAINTENANCE_TABLE_KINDS:
            return True

        chunk_type = str(source.chunk_type or "").strip().lower()
        if chunk_type in _HIGH_SIGNAL_CHUNK_TYPES:
            return True

        text = self._source_text(source)
        has_interval_signal = mentions_maintenance_interval(text) or bool(
            _INTERVAL_PATTERN.search(text)
        )
        has_action_signal = bool(_ACTION_PATTERN.search(text))
        has_maintenance_marker = any(marker in text for marker in _MAINTENANCE_MARKERS)

        if has_interval_signal and (has_action_signal or has_maintenance_marker):
            return True
        if has_maintenance_marker and has_action_signal:
            return True
        if chunk_type in _LOW_SIGNAL_CHUNK_TYPES:
            return False
        return has_interval_signal or (has_maintenance_marker and has_action_signal)

    @staticmethod
    def _source_text(source: AnswerSource) -> str:
        parts = [
            str(source.chunk_name or "").strip(),
            str(source.section_path or "").strip(),
            str(source.content or "").strip(),
        ]
        if source.table_rows:
            parts.extend(
                " ".join(str(cell).strip() for cell in row if str(cell).strip())
                for row in source.table_rows
            )
        normalized = " ".join(part for part in parts if part)
        return " ".join(normalized.lower().split())
