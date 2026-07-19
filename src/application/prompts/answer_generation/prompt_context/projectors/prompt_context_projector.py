from src.application.prompts.answer_generation.prompt_context.canonicalization.prompt_evidence_canonicalizer import (
    PromptEvidenceCanonicalizer,
)
from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptEntityView,
    PromptRelationshipView,
    PromptSectionGroupView,
    PromptSourceGroupView,
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.relationships.prompt_relationship_graph_builder import (
    PromptRelationshipGraphBuilder,
)
from src.application.prompts.answer_generation.prompt_context.tables.prompt_table_projector import (
    PromptTableProjector,
)
from src.application.prompts.answer_generation.prompt_context.topology.prompt_evidence_topology_builder import (
    PromptEvidenceTopologyBuilder,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)


class PromptContextProjector:
    def __init__(
        self,
        prompt_evidence_canonicalizer: PromptEvidenceCanonicalizer | None = None,
        prompt_relationship_graph_builder: PromptRelationshipGraphBuilder | None = None,
        prompt_table_projector: PromptTableProjector | None = None,
        prompt_evidence_topology_builder: PromptEvidenceTopologyBuilder | None = None,
    ) -> None:
        self.prompt_evidence_canonicalizer = (
            prompt_evidence_canonicalizer or PromptEvidenceCanonicalizer()
        )
        self.prompt_relationship_graph_builder = (
            prompt_relationship_graph_builder or PromptRelationshipGraphBuilder()
        )
        self.prompt_table_projector = prompt_table_projector or PromptTableProjector()
        self.prompt_evidence_topology_builder = (
            prompt_evidence_topology_builder or PromptEvidenceTopologyBuilder()
        )

    def project(
        self,
        context: StructuredAnswerContext | None,
    ) -> PromptContextBundle | None:
        if context is None:
            return None
        projected_sources = [self._project_source(source) for source in context.sources]
        projected_entities = [
            self._project_entity(entity) for entity in context.structured_entities
        ]
        source_number_by_chunk_id = {
            source.chunk_id: source.source_number
            for source in projected_sources
            if source.chunk_id
        }
        relationship_edges, relationship_families = (
            self.prompt_relationship_graph_builder.build(
                projected_entities,
                source_number_by_chunk_id=source_number_by_chunk_id,
            )
        )
        tables = self.prompt_table_projector.build_from_answer_tables(context.tables)
        # Per-source fallback, not all-or-nothing: `build_from_answer_tables`
        # silently drops any AnswerTable whose projection came out empty
        # (canonicalization stripped every row, no headers/rows survived,
        # etc.) -- if that happens for one source while a DIFFERENT source's
        # table projects fine, `tables` is non-empty overall, so the old
        # `if not tables:` guard never gave the failed source a second
        # chance. Building the raw-row fallback only for sources not already
        # covered by a projected table closes that gap (finding F8,
        # outputs/architecture/answering_and_prompt_fresh_audit.md) while
        # leaving the fully-empty case (every source falls through) with the
        # exact same practical outcome as before.
        covered_chunk_ids = {table.chunk_id for table in tables}
        uncovered_sources = [
            source
            for source in projected_sources
            if source.chunk_id not in covered_chunk_ids
        ]
        if uncovered_sources:
            tables = [
                *tables,
                *self.prompt_table_projector.build(uncovered_sources),
            ]
        source_families, section_topology = self.prompt_evidence_topology_builder.build(
            answer_intent_value=context.answer_intent.value,
            sources=projected_sources,
            tables=tables,
        )
        return self.prompt_evidence_canonicalizer.canonicalize(
            PromptContextBundle(
                answer_intent_value=context.answer_intent.value,
                source_count=context.source_count,
                sources=list(projected_sources),
                appendix_sources=list(projected_sources),
                key_values=list(context.key_values),
                maintenance_entries=list(context.maintenance_entries),
                tables=tables,
                entities=projected_entities,
                relationship_edges=relationship_edges,
                relationship_families=relationship_families,
                source_families=source_families,
                section_topology=section_topology,
                source_groups=[
                    PromptSourceGroupView(
                        group_name=group.group_name,
                        chunk_type=group.chunk_type,
                        source_numbers=[
                            source.source_number for source in group.sources
                        ],
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
            table_shape=source.table_shape,
            table_structure_quality=source.table_structure_quality,
            table_header_paths=[list(path) for path in source.table_header_paths],
            table_axis_summary=dict(source.table_axis_summary),
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
