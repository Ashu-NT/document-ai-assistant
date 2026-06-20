from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.domain.common import DocumentType


@dataclass(slots=True, frozen=True)
class DocumentTypeDecision:
    effective_document_type: DocumentType
    effective_chunking_profile: ChunkingProfile
    confidence: float
    reasons: list[str] = field(default_factory=list)
    should_rechunk: bool = False
