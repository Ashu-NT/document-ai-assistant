from src.application.services.extraction import ExtractionService
from src.application.workflows.linking.contact_point_relationship_candidate_builder import (
    ContactPointRelationshipCandidateBuilder,
)
from src.application.workflows.linking.semantic_entity_index import (
    IndexedEntity,
    SemanticEntityIndex,
)
from src.application.workflows.linking.semantic_relationship_candidate_generator import (
    RelationshipCandidate,
    SemanticRelationshipCandidateGenerator,
    generate_fk_passthrough_candidates,
)
from src.application.workflows.linking.semantic_relationship_scorer import resolve_status
from src.domain.extraction import (
    SemanticEntityType,
    SemanticRelationship,
    SemanticSourceMetadata,
)
from src.shared.ids import IdGenerator


class SemanticLinkingWorkflow:
    """Discovers and persists relationships between a document's
    already-extracted semantic entities, so retrieval can traverse related
    entities (e.g. a maintenance task's procedure, required spare parts, and
    safety warnings) instead of only the chunk that was matched.

    Runs as a standalone, explicitly-invoked step per `document_id` — it is
    not wired into `IngestionWorkflow`'s default pipeline, matching this
    codebase's convention for new, not-yet-validated post-extraction
    features (see `EXTRACTION_CANDIDATE_NARROWING_ENABLED`).

    Re-running `link()` for the same document is idempotent: relationships
    are replaced wholesale for that `document_id`.
    """

    def __init__(
        self,
        *,
        extraction_service: ExtractionService,
        id_generator: IdGenerator,
    ) -> None:
        self.extraction_service = extraction_service
        self.id_generator = id_generator
        self.candidate_generator = SemanticRelationshipCandidateGenerator()
        self.contact_point_candidate_builder = (
            ContactPointRelationshipCandidateBuilder()
        )

    def link(self, document_id: str) -> list[SemanticRelationship]:
        maintenance_tasks = self.extraction_service.list_maintenance_tasks(document_id)
        maintenance_intervals = self.extraction_service.list_maintenance_intervals(
            document_id
        )
        procedures = self.extraction_service.list_procedures(document_id)
        spare_parts = self.extraction_service.list_spare_parts(document_id)
        safety_warnings = self.extraction_service.list_safety_warnings(document_id)
        equipment = self.extraction_service.list_equipment(document_id)
        manufacturers = self.extraction_service.list_manufacturers(document_id)
        suppliers = self.extraction_service.list_suppliers(document_id)
        contact_points = self.extraction_service.list_contact_points(document_id)
        specifications = self.extraction_service.list_specifications(document_id)
        troubleshooting_entries = self.extraction_service.list_troubleshooting_entries(
            document_id
        )

        fk_candidates = generate_fk_passthrough_candidates(
            maintenance_tasks=maintenance_tasks,
            maintenance_intervals=maintenance_intervals,
            equipment=equipment,
            procedures=procedures,
            troubleshooting_entries=troubleshooting_entries,
        )

        indexed_entities = self._build_index(
            maintenance_tasks=maintenance_tasks,
            procedures=procedures,
            spare_parts=spare_parts,
            safety_warnings=safety_warnings,
            equipment=equipment,
            specifications=specifications,
        )
        proximity_candidates = self.candidate_generator.generate(
            SemanticEntityIndex(indexed_entities)
        )
        ownership_candidates = self.contact_point_candidate_builder.build(
            contact_points=contact_points,
            manufacturers=manufacturers,
            suppliers=suppliers,
        )

        relationships = self._resolve_relationships(
            document_id,
            fk_candidates + proximity_candidates + ownership_candidates,
        )

        self.extraction_service.replace_semantic_relationships(
            document_id, relationships
        )

        return relationships

    @staticmethod
    def _build_index(
        *,
        maintenance_tasks,
        procedures,
        spare_parts,
        safety_warnings,
        equipment,
        specifications,
    ) -> list[IndexedEntity]:
        sources: list[tuple[SemanticEntityType, str, SemanticSourceMetadata | None]] = [
            (SemanticEntityType.MAINTENANCE_TASK, task.task_id, task.source_metadata)
            for task in maintenance_tasks
        ]
        sources += [
            (SemanticEntityType.PROCEDURE, procedure.procedure_id, procedure.source_metadata)
            for procedure in procedures
        ]
        sources += [
            (SemanticEntityType.SPARE_PART, part.spare_part_id, part.source_metadata)
            for part in spare_parts
        ]
        sources += [
            (
                SemanticEntityType.SAFETY_WARNING,
                warning.safety_warning_id,
                warning.source_metadata,
            )
            for warning in safety_warnings
        ]
        sources += [
            (SemanticEntityType.EQUIPMENT, item.equipment_id, item.source_metadata)
            for item in equipment
        ]
        sources += [
            (
                SemanticEntityType.SPECIFICATION,
                specification.specification_id,
                specification.source_metadata,
            )
            for specification in specifications
        ]

        indexed = (
            IndexedEntity.from_source_metadata(entity_type, entity_id, source_metadata)
            for entity_type, entity_id, source_metadata in sources
        )
        return [entity for entity in indexed if entity is not None]

    def _resolve_relationships(
        self,
        document_id: str,
        candidates: list[RelationshipCandidate],
    ) -> list[SemanticRelationship]:
        relationships: list[SemanticRelationship] = []

        for candidate in candidates:
            status = resolve_status(candidate.score)
            if status is None:
                continue

            relationships.append(
                SemanticRelationship(
                    relationship_id=self.id_generator.new_id("semantic_relationship"),
                    document_id=document_id,
                    relationship_type=candidate.relationship_type,
                    source_entity_type=candidate.source_entity_type,
                    source_entity_id=candidate.source_entity_id,
                    target_entity_type=candidate.target_entity_type,
                    target_entity_id=candidate.target_entity_id,
                    confidence_score=candidate.score,
                    status=status,
                    evidence=candidate.evidence,
                )
            )

        return relationships
