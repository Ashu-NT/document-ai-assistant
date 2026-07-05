from dataclasses import dataclass, field
from enum import StrEnum

from src.domain.common import AuditMetadata


class SemanticEntityType(StrEnum):
    """Identifies which extraction entity table a relationship endpoint points at.

    Kept local to the domain layer (rather than reusing
    `ExtractionPromptType` from the application layer) to avoid an inverted
    dependency; values are chosen to match that enum's strings by
    convention so the two stay interchangeable at the value level.
    """

    MAINTENANCE_TASK = "maintenance_task"
    MAINTENANCE_INTERVAL = "maintenance_interval"
    PROCEDURE = "procedure"
    SPARE_PART = "spare_part"
    EQUIPMENT = "equipment"
    MANUFACTURER = "manufacturer"
    SUPPLIER = "supplier"
    SPECIFICATION = "specification"
    SAFETY_WARNING = "safety_warning"
    TROUBLESHOOTING_ENTRY = "troubleshooting_entry"


class SemanticRelationshipType(StrEnum):
    TASK_HAS_INTERVAL = "task_has_interval"
    TASK_USES_PROCEDURE = "task_uses_procedure"
    TASK_REQUIRES_SPARE_PART = "task_requires_spare_part"
    TASK_REQUIRES_SAFETY_WARNING = "task_requires_safety_warning"
    EQUIPMENT_HAS_PROCEDURE = "equipment_has_procedure"
    EQUIPMENT_HAS_SPARE_PART = "equipment_has_spare_part"
    EQUIPMENT_HAS_SPECIFICATION = "equipment_has_specification"
    EQUIPMENT_HAS_TROUBLESHOOTING_ENTRY = "equipment_has_troubleshooting_entry"


class SemanticRelationshipStatus(StrEnum):
    ACCEPTED = "accepted"
    NEEDS_REVIEW = "needs_review"


@dataclass(slots=True)
class SemanticRelationship:
    relationship_id: str
    document_id: str

    relationship_type: SemanticRelationshipType

    source_entity_type: SemanticEntityType
    source_entity_id: str
    target_entity_type: SemanticEntityType
    target_entity_id: str

    confidence_score: float
    status: SemanticRelationshipStatus = SemanticRelationshipStatus.NEEDS_REVIEW
    evidence: str | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)
