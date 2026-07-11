from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models import (
    PromptEntityView,
    PromptEvidenceFamilyView,
    PromptRelationshipEdgeView,
)


class PromptRelationshipGraphBuilder:
    def build(
        self,
        entities: list[PromptEntityView],
        *,
        source_number_by_chunk_id: dict[str, int],
    ) -> tuple[list[PromptRelationshipEdgeView], list[PromptEvidenceFamilyView]]:
        edges: list[PromptRelationshipEdgeView] = []
        families: list[PromptEvidenceFamilyView] = []
        edge_counter = 0
        family_counter = 0
        for entity in entities:
            if not entity.relationships:
                continue
            family_counter += 1
            family_id = f"family_{family_counter}"
            anchor_source_number = source_number_by_chunk_id.get(
                entity.source_chunk_id or ""
            )
            family_edge_ids: list[str] = []
            relationship_types: list[str] = []
            related_entity_ids: list[str] = []
            related_entity_types: list[str] = []
            for relationship in entity.relationships:
                edge_counter += 1
                edge_id = f"edge_{edge_counter}"
                family_edge_ids.append(edge_id)
                relationship_types.append(relationship.relationship_type)
                related_entity_ids.append(relationship.target_entity_id)
                related_entity_types.append(relationship.target_entity_type)
                edges.append(
                    PromptRelationshipEdgeView(
                        edge_id=edge_id,
                        source_entity_type=entity.entity_type,
                        source_entity_id=entity.entity_id,
                        source_chunk_id=entity.source_chunk_id,
                        source_number=anchor_source_number,
                        relationship_type=relationship.relationship_type,
                        direction=relationship.direction,
                        status=relationship.status,
                        confidence_score=relationship.confidence_score,
                        target_entity_type=relationship.target_entity_type,
                        target_entity_id=relationship.target_entity_id,
                        target_entity_fields=dict(relationship.target_entity_fields),
                    )
                )
            families.append(
                PromptEvidenceFamilyView(
                    family_id=family_id,
                    anchor_entity_type=entity.entity_type,
                    anchor_entity_id=entity.entity_id,
                    anchor_source_number=anchor_source_number,
                    edge_ids=family_edge_ids,
                    relationship_types=self._unique_in_order(relationship_types),
                    related_entity_ids=self._unique_in_order(related_entity_ids),
                    related_entity_types=self._unique_in_order(related_entity_types),
                )
            )
        return edges, families

    @staticmethod
    def _unique_in_order(values: list[str]) -> list[str]:
        unique: list[str] = []
        seen: set[str] = set()
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            unique.append(value)
        return unique
