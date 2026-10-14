from __future__ import annotations

from dataclasses import replace as dataclass_replace
from typing import Any

from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.builders.maintenance_task_code_grounding import (
    verify_task_code_against_canonical_row,
)
from src.domain.assets import TableAsset
from src.domain.document import DocumentChunk
from src.domain.extraction import MaintenanceTask
from src.shared.ids import IdGenerator


class MaintenanceTaskBuilder:
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
        tables: dict[str, TableAsset] | None = None,
    ) -> MaintenanceTask:
        support = self._support
        title = support.required_text(
            payload,
            field_name="maintenance_tasks.title",
            keys=("title", "task", "name"),
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
            item_type="maintenance_tasks",
        )

        claimed_task_code = support.optional_text(payload, "task_code", "code", "task_reference")
        verified_task_code: str | None = None
        code_unverified = False
        if claimed_task_code is not None:
            source_chunk = (
                chunk_lookup.get(source_chunk_id)
                if source_chunk_id is not None and not chunk_id_invalid
                else None
            )
            if source_chunk is not None and verify_task_code_against_canonical_row(
                task_code=claimed_task_code,
                title=title,
                source_chunk=source_chunk,
                tables=tables,
            ):
                verified_task_code = claimed_task_code
            else:
                code_unverified = True
                support.maintenance_task_unverified_code_events.append(
                    {"source_chunk_id": source_chunk_id, "claimed_task_code": claimed_task_code}
                )

        source_metadata = support.build_source_metadata(
            source_chunk_id=source_chunk_id,
            chunk_lookup=chunk_lookup,
        )
        if source_metadata is not None and verified_task_code is not None:
            source_metadata = dataclass_replace(source_metadata, table_row_id=verified_task_code)

        return MaintenanceTask(
            task_id=self._id_generator.new_id("task"),
            document_id=document_id,
            title=title,
            description=support.optional_text(payload, "description", "details"),
            interval=support.optional_text(payload, "interval", "frequency"),
            component_name=support.optional_text(payload, "component_name", "component"),
            equipment_id=support.optional_text(payload, "equipment_id"),
            task_code=verified_task_code,
            source_chunk_id=source_chunk_id,
            source=support.resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            source_metadata=source_metadata,
            confidence_score=confidence_score,
            requires_human_review=(
                support.resolve_requires_human_review(
                    support.pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
                or code_unverified
            ),
        )
