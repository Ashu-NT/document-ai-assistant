from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptEntityView,
    PromptRelationshipView,
    PromptSectionGroupView,
    PromptSourceGroupView,
    PromptSourceView,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)


class PromptContextProjector:
    def project(
        self,
        context: StructuredAnswerContext | None,
    ) -> PromptContextBundle | None:
        if context is None:
            return None
        return PromptContextBundle(
            answer_intent_value=context.answer_intent.value,
            source_count=context.source_count,
            sources=[self._project_source(source) for source in context.sources],
            key_values=list(context.key_values),
            maintenance_entries=list(context.maintenance_entries),
            entities=[self._project_entity(entity) for entity in context.structured_entities],
            source_groups=[
                PromptSourceGroupView(
                    group_name=group.group_name,
                    chunk_type=group.chunk_type,
                    source_numbers=[source.source_number for source in group.sources],
                )
                for group in context.source_groups
            ],
            section_groups=[
                PromptSectionGroupView(
                    group_name=group.group_name,
                    section_path=group.section_path,
                    page_start=group.page_start,
                    page_end=group.page_end,
                    source_numbers=list(group.source_numbers),
                )
                for group in context.section_groups
            ],
            diagnostics=dict(context.diagnostics),
        )

    @staticmethod
    def _project_source(source) -> PromptSourceView:
        return PromptSourceView(
            source_number=source.source_number,
            chunk_id=source.chunk_id,
            chunk_name=source.chunk_name,
            chunk_type=source.chunk_type,
            document_id=source.document_id,
            document_title=source.document_title or "Current document",
            section_path=source.section_path or "N/A",
            page_start=source.page_start,
            page_end=source.page_end,
            score=source.score,
            content=source.content,
            table_rows=source.table_rows,
            retrieval_source=source.retrieval_source,
            section_id=source.section_id,
            metadata=dict(source.metadata),
            identifier_values=list(source.identifier_values),
            collapsed_chunk_ids=list(source.collapsed_chunk_ids),
        )

    def _project_entity(self, entity) -> PromptEntityView:
        return PromptEntityView(
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            fields=dict(entity.fields),
            source_chunk_id=entity.source_chunk_id,
            relationships=[
                PromptRelationshipView(
                    relationship_type=relationship.relationship_type,
                    direction=relationship.direction,
                    status=relationship.status,
                    target_entity_type=relationship.target_entity_type,
                    target_entity_id=relationship.target_entity_id,
                    confidence_score=relationship.confidence_score,
                    target_entity_fields=dict(relationship.target_entity_fields),
                )
                for relationship in entity.relationships
            ],
        )
