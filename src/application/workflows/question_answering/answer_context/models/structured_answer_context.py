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
from src.application.workflows.question_answering.answer_context.models.answer_structured_entity import (
    AnswerStructuredEntity,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
)


@dataclass(slots=True)
class StructuredAnswerContext:
    answer_intent: AnswerIntent
    sources: list[AnswerSource] = field(default_factory=list)
    tables: list[AnswerTable] = field(default_factory=list)
    source_groups: list[AnswerSourceGroup] = field(default_factory=list)
    section_groups: list[AnswerSectionGroup] = field(default_factory=list)
    key_values: list[AnswerKeyValue] = field(default_factory=list)
    maintenance_entries: list[AnswerMaintenanceEntry] = field(default_factory=list)
    structured_entities: list[AnswerStructuredEntity] = field(default_factory=list)
    source_count: int = 0
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def entities_of_type(self, entity_type: str) -> list[AnswerStructuredEntity]:
        return [
            entity
            for entity in self.structured_entities
            if entity.entity_type == entity_type
        ]
