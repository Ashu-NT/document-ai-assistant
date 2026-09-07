from collections.abc import Mapping
from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_evidence_matcher import (
    StructuralEvidenceSummary,
)


@dataclass(slots=True, frozen=True)
class StructuralDocumentFeatures:
    element_count: int = 0
    section_count: int = 0
    root_section_count: int = 0
    nested_section_count: int = 0
    max_section_depth: int = 1

    text_element_count: int = 0

    avg_text_tokens: float = 0.0
    table_ratio: float = 0.0
    picture_ratio: float = 0.0
    list_ratio: float = 0.0
    caption_ratio: float = 0.0
    nested_section_ratio: float = 0.0
    long_text_ratio: float = 0.0
    short_text_ratio: float = 0.0

    # Per-profile title-keyword evidence (a crude substring search, see
    # StructuralEvidenceMatcher) feeding the signal used by
    # StructuralProfileInferer/HybridDocumentTypeResolver -- deliberately
    # separate from the unrelated, much richer EvidenceMarker/MarkerStrength
    # system under chunking/builders/structured/markers, which scores
    # evidence within already-classified section content, not raw title
    # term density across a whole document.
    evidence: Mapping[ChunkingProfile, StructuralEvidenceSummary] = field(
        default_factory=dict
    )
    procedure_like_section_count: int = 0
