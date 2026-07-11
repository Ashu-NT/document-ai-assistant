from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.prompts.answer_generation.prompt_context.models.prompt_entity_view import (
    PromptEntityView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_group_views import (
    PromptSectionGroupView,
    PromptSourceGroupView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
)


@dataclass(slots=True, frozen=True)
class PromptContextBundle:
    answer_intent_value: str
    source_count: int
    sources: list[PromptSourceView] = field(default_factory=list)
    appendix_sources: list[PromptSourceView] = field(default_factory=list)
    key_values: list[AnswerKeyValue] = field(default_factory=list)
    maintenance_entries: list[AnswerMaintenanceEntry] = field(default_factory=list)
    entities: list[PromptEntityView] = field(default_factory=list)
    source_groups: list[PromptSourceGroupView] = field(default_factory=list)
    section_groups: list[PromptSectionGroupView] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
