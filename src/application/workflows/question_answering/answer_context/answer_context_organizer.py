from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.key_value_extractor import (
    KeyValueExtractor,
)
from src.application.workflows.question_answering.answer_context.maintenance.maintenance_task_extractor import (
    MaintenanceTaskExtractor,
)
from src.application.workflows.question_answering.answer_context.maintenance_entry_merger import (
    MaintenanceEntryMerger,
)
from src.application.workflows.question_answering.answer_context.section_group_builder import (
    SectionGroupBuilder,
)
from src.application.workflows.question_answering.answer_context.source_group_builder import (
    SourceGroupBuilder,
)
from src.application.workflows.question_answering.answer_context.structured_source_builder import (
    StructuredSourceBuilder,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class AnswerContextOrganizer:
    def __init__(
        self,
        *,
        key_value_extractor: KeyValueExtractor | None = None,
        maintenance_task_extractor: MaintenanceTaskExtractor | None = None,
        maintenance_entry_merger: MaintenanceEntryMerger | None = None,
        source_group_builder: SourceGroupBuilder | None = None,
        section_group_builder: SectionGroupBuilder | None = None,
        structured_source_builder: StructuredSourceBuilder | None = None,
    ) -> None:
        self.key_value_extractor = key_value_extractor or KeyValueExtractor()
        self.maintenance_task_extractor = (
            maintenance_task_extractor or MaintenanceTaskExtractor()
        )
        self.maintenance_entry_merger = (
            maintenance_entry_merger or MaintenanceEntryMerger()
        )
        self.source_group_builder = source_group_builder or SourceGroupBuilder()
        self.section_group_builder = section_group_builder or SectionGroupBuilder()
        self.structured_source_builder = (
            structured_source_builder or StructuredSourceBuilder()
        )

    def organize(
        self,
        *,
        answer_intent: AnswerIntent,
        chunks: Sequence[RetrievedChunk],
    ) -> StructuredAnswerContext:
        sources = self.structured_source_builder.build_sources(chunks)
        source_groups = self.source_group_builder.build(sources)
        section_groups = self.section_group_builder.build(sources)
        key_values = self.key_value_extractor.extract(
            sources,
            answer_intent=answer_intent,
        )
        maintenance_entries = self.maintenance_task_extractor.extract_maintenance_entries(
            sources,
            answer_intent=answer_intent,
        )
        extracted_maintenance_entry_count = len(maintenance_entries)
        maintenance_entries = self.maintenance_entry_merger.merge(maintenance_entries)
        maintenance_with_interval = sum(
            1
            for entry in maintenance_entries
            if entry.interval.strip().lower() != "not specified"
        )
        diagnostics = {
            "chunk_type_counts": dict(
                Counter(source.chunk_type or "unknown" for source in sources)
            ),
            "section_group_count": len(section_groups),
            "document_ids": sorted(
                {
                    source.document_id
                    for source in sources
                    if source.document_id
                }
            ),
            "maintenance_items_found": len(maintenance_entries),
            "maintenance_items_with_interval": maintenance_with_interval,
            "maintenance_items_without_interval": (
                len(maintenance_entries) - maintenance_with_interval
            ),
            "maintenance_items_merged": (
                extracted_maintenance_entry_count - len(maintenance_entries)
            ),
        }
        return StructuredAnswerContext(
            answer_intent=answer_intent,
            sources=sources,
            source_groups=source_groups,
            section_groups=section_groups,
            key_values=key_values,
            maintenance_entries=maintenance_entries,
            source_count=len(sources),
            diagnostics=diagnostics,
        )
