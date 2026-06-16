from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, ModelProcessingMetadata


@dataclass(slots=True)
class ClassificationResult:
    classification_id: str
    document_id: str

    predicted_label: str
    confidence_score: float | None = None

    rationale: str | None = None
    evidence: list[str] = field(default_factory=list)

    processing_metadata: ModelProcessingMetadata | None = None
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def is_confident(self, threshold: float) -> bool:
        if self.confidence_score is None:
            return False
        return self.confidence_score >= threshold