from __future__ import annotations

from collections import Counter
import inspect
from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.evidence_contradiction_detector import (
    EvidenceContradictionDetector,
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
from src.application.workflows.question_answering.answer_context.tables.answer_table_projector import (
    AnswerTableProjector,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)
from src.domain.document.entities.identifier import Identifier
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
        answer_table_projector: AnswerTableProjector | None = None,
        evidence_contradiction_detector: EvidenceContradictionDetector | None = None,
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
        self.answer_table_projector = answer_table_projector or AnswerTableProjector()
        self.evidence_contradiction_detector = (
            evidence_contradiction_detector or EvidenceContradictionDetector()
        )

    def organize(
        self,
        *,
        answer_intent: AnswerIntent,
        chunks: Sequence[RetrievedChunk],
        resolved_identifiers: Sequence[Identifier] = (),
    ) -> StructuredAnswerContext:
        sources = self.structured_source_builder.build_sources(chunks)
        tables = self.answer_table_projector.build(sources)
        source_groups = self.source_group_builder.build(sources)
        section_groups = self.section_group_builder.build(sources)
        key_values = self.key_value_extractor.extract(
            sources,
            **self._extractor_kwargs(
                self.key_value_extractor.extract,
                answer_intent=answer_intent,
                tables=tables,
            ),
        )
        maintenance_entries = self.maintenance_task_extractor.extract_maintenance_entries(
            sources,
            **self._extractor_kwargs(
                self.maintenance_task_extractor.extract_maintenance_entries,
                answer_intent=answer_intent,
                tables=tables,
            ),
        )
        extracted_maintenance_entry_count = len(maintenance_entries)
        maintenance_entries = self.maintenance_entry_merger.merge(maintenance_entries)
        maintenance_with_interval = sum(
            1
            for entry in maintenance_entries
            if entry.interval.strip().lower() != "not specified"
        )
        evidence_conflicts = self.evidence_contradiction_detector.detect(
            key_values=key_values,
            maintenance_entries=maintenance_entries,
            sources=sources,
            resolved_identifiers=resolved_identifiers,
        )
        diagnostics = {
            "chunk_type_counts": dict(
                Counter(source.chunk_type or "unknown" for source in sources)
            ),
            "section_group_count": len(section_groups),
            "table_count": len(tables),
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
            "evidence_conflicts": [
                {
                    "key": conflict.key,
                    "field_kind": conflict.field_kind,
                    "values": list(conflict.values),
                    "source_numbers": list(conflict.source_numbers),
                    "is_critical": conflict.is_critical,
                    "document_ids": list(conflict.document_ids),
                }
                for conflict in evidence_conflicts
            ],
            "has_critical_evidence_conflict": any(
                conflict.is_critical for conflict in evidence_conflicts
            ),
        }
        return StructuredAnswerContext(
            answer_intent=answer_intent,
            sources=sources,
            tables=tables,
            source_groups=source_groups,
            section_groups=section_groups,
            key_values=key_values,
            maintenance_entries=maintenance_entries,
            source_count=len(sources),
            diagnostics=diagnostics,
        )

    @staticmethod
    def _extractor_kwargs(callable_obj, **kwargs):
        supported = inspect.signature(callable_obj).parameters
        return {
            key: value for key, value in kwargs.items() if key in supported
        }
