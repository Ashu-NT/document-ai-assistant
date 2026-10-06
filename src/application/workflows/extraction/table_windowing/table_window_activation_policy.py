from __future__ import annotations

from dataclasses import dataclass

from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.workflows.extraction.extraction_execution_strategy import (
    ExtractionExecutionStrategy,
)
from src.application.workflows.extraction.table_payload.table_payload_support import (
    TablePayloadSupport,
)
from src.domain.assets import TableAsset

# Deliberately separate from TableEvidenceWindowBuilder (the generic
# mechanism): this is the narrow, experiment-specific POLICY deciding WHEN
# windowing activates. "BUILD THE MECHANISM GENERICALLY. VALIDATE THE
# POLICY NARROWLY." - a future family's activation is meant to be a change
# to `activated_entity_types` (or a new policy instance), never a rewrite
# of the windowing mechanism itself.


@dataclass(slots=True, frozen=True)
class TableWindowActivationPolicy:
    enabled: bool
    rows_per_window: int
    activated_entity_types: frozenset[ExtractionPromptType] = frozenset(
        {ExtractionPromptType.MAINTENANCE_TASK}
    )

    def should_window(
        self,
        *,
        entity_type: ExtractionPromptType,
        execution_strategy: ExtractionExecutionStrategy,
        table: TableAsset | None,
        support: TablePayloadSupport | None = None,
    ) -> bool:
        if not self.enabled:
            return False
        if execution_strategy is not ExtractionExecutionStrategy.SPECIALIZED_FAMILY:
            return False
        if entity_type not in self.activated_entity_types:
            return False
        if table is None:
            return False

        resolved_support = support or TablePayloadSupport()
        cleaned_rows = resolved_support.cleaned_rows(table)
        data_row_count = max(0, len(cleaned_rows) - 1)
        return data_row_count > self.rows_per_window
