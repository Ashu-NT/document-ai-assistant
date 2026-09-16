from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference import (
    StructuralProfileInference,
)
from src.domain.document import DocumentChunk


@dataclass(slots=True, frozen=True)
class GraphChunkBuildResult:
    """What GraphChunkBuilder.build_chunks() returns: the materialized
    chunks plus the structural-profile inference produced while building
    them, bundled explicitly instead of stashed on a `last_*` instance
    attribute (see SectionChunkBuildResult - this is the same fix one
    layer up the call chain)."""

    chunks: list[DocumentChunk]
    structural_inference: StructuralProfileInference | None = None


__all__ = ["GraphChunkBuildResult"]
