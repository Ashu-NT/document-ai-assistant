from __future__ import annotations

from collections import Counter
from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.key_value_extractor import (
    KeyValueExtractor,
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
from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerSource,
    StructuredAnswerContext,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class AnswerContextOrganizer:
    def __init__(
        self,
        *,
        key_value_extractor: KeyValueExtractor | None = None,
        maintenance_entry_merger: MaintenanceEntryMerger | None = None,
        source_group_builder: SourceGroupBuilder | None = None,
        section_group_builder: SectionGroupBuilder | None = None,
    ) -> None:
        self.key_value_extractor = key_value_extractor or KeyValueExtractor()
        self.maintenance_entry_merger = (
            maintenance_entry_merger or MaintenanceEntryMerger()
        )
        self.source_group_builder = source_group_builder or SourceGroupBuilder()
        self.section_group_builder = section_group_builder or SectionGroupBuilder()

    def organize(
        self,
        *,
        answer_intent: AnswerIntent,
        chunks: Sequence[RetrievedChunk],
    ) -> StructuredAnswerContext:
        sources = [
            self._to_source(index + 1, chunk)
            for index, chunk in enumerate(chunks)
        ]
        source_groups = self.source_group_builder.build(sources)
        section_groups = self.section_group_builder.build(sources)
        key_values = self.key_value_extractor.extract(
            sources,
            answer_intent=answer_intent,
        )
        maintenance_entries = self.key_value_extractor.extract_maintenance_entries(
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

    @staticmethod
    def _to_source(source_number: int, chunk: RetrievedChunk) -> AnswerSource:
        citation = chunk.citation
        section_path = " > ".join(chunk.section_path) if chunk.section_path else None
        chunk_name = (
            (citation.section_title if citation is not None else None)
            or (chunk.section_path[-1] if chunk.section_path else None)
            or chunk.chunk_type.value
        )
        document_title = None
        if citation is not None and citation.document_name:
            document_title = citation.document_name
        elif chunk.metadata.get("document_title"):
            document_title = chunk.metadata["document_title"]
        return AnswerSource(
            source_number=source_number,
            chunk_id=chunk.chunk_id,
            chunk_name=chunk_name,
            chunk_type=chunk.chunk_type.value,
            document_id=chunk.document_id,
            document_title=document_title,
            section_path=section_path,
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
            score=chunk.score,
            content=chunk.content,
        )
