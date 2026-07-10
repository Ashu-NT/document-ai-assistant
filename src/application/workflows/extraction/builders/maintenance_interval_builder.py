from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.extraction_reference_resolver import (
    resolve_maintenance_task_id,
)
from src.domain.document import DocumentChunk
from src.domain.extraction import MaintenanceInterval, MaintenanceTask
from src.shared.ids import IdGenerator


class MaintenanceIntervalBuilder:
    def __init__(
        self,
        id_generator: IdGenerator,
        support: ExtractionBuilderSupport,
    ) -> None:
        self._id_generator = id_generator
        self._support = support

    def build(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
        maintenance_tasks: list[MaintenanceTask],
    ) -> MaintenanceInterval:
        support = self._support
        interval = support.required_text(
            payload,
            field_name="maintenance_intervals.interval",
            keys=("interval",),
        )
        confidence_score = support.parse_confidence(
            support.pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = support.resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="maintenance_intervals",
        )

        task_reference = support.optional_text(payload, "task_reference")
        maintenance_task_id = resolve_maintenance_task_id(
            task_reference,
            maintenance_tasks,
        )

        return MaintenanceInterval(
            maintenance_interval_id=self._id_generator.new_id("maintenance_interval"),
            document_id=document_id,
            interval=interval,
            component_name=support.optional_text(payload, "component_name", "component"),
            maintenance_task_id=maintenance_task_id,
            source_chunk_id=source_chunk_id,
            source=support.resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            source_metadata=support.build_source_metadata(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                support.resolve_requires_human_review(
                    support.pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )
