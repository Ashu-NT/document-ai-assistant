from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_evidence_family import (
    StructuredEvidenceFamily,
)
from src.domain.common import ChunkType


@dataclass(slots=True, frozen=True)
class StructuredSectionWindowSpec:
    family: StructuredEvidenceFamily
    section_path: list[str]
    anchor_markers: tuple[EvidenceMarker, ...]

    chunk_type: ChunkType = ChunkType.GENERAL
    radius_before: int = 0
    radius_after: int = 8
    min_tokens: int = 6
    combine_all_windows: bool = False
    include_full_section_if_no_anchor: bool = False
    section_context_matches: bool = False