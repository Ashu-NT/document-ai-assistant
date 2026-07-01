from dataclasses import dataclass, field

from src.domain.common import AuditMetadata


@dataclass(slots=True)
class ExtractedIdentifier:
    """An identifier the LLM extracted directly from chunk text.

    Unlike structured entities (SparePart, EquipmentInfo), this carries any
    typed identifier the LLM found — drawing numbers, certificate numbers,
    tag numbers, order codes, etc. — that don't map to a richer entity.
    IdentifierPromotionService promotes these into Identifier domain objects.
    """

    raw_value: str
    identifier_type: str

    source_chunk_id: str | None = None
    confidence_score: float | None = None
    requires_human_review: bool = True

    audit: AuditMetadata = field(default_factory=AuditMetadata)
