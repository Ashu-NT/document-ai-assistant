from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.models.answer_groups import (
    AnswerSectionGroup,
    AnswerSourceGroup,
)
from src.application.workflows.question_answering.answer_context.models.answer_key_value import (
    AnswerKeyValue,
)
from src.application.workflows.question_answering.answer_context.models.answer_maintenance_entry import (
    AnswerMaintenanceEntry,
)
from src.application.workflows.question_answering.answer_context.models.answer_source import (
    AnswerSource,
)


@dataclass(slots=True)
class StructuredAnswerContext:
    answer_intent: AnswerIntent
    sources: list[AnswerSource] = field(default_factory=list)
    source_groups: list[AnswerSourceGroup] = field(default_factory=list)
    section_groups: list[AnswerSectionGroup] = field(default_factory=list)
    key_values: list[AnswerKeyValue] = field(default_factory=list)
    maintenance_entries: list[AnswerMaintenanceEntry] = field(default_factory=list)
    source_count: int = 0
    diagnostics: dict[str, Any] = field(default_factory=dict)
