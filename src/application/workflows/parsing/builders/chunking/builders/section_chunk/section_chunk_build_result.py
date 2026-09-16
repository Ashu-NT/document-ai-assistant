from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.models import ChunkPayload
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference import (
    StructuralProfileInference,
)


@dataclass(slots=True, frozen=True)
class SectionChunkBuildResult:
    """What SectionChunkBuilder's build methods return: the computed chunk
    payloads plus the structural-profile inference produced as a side
    effect of building them, bundled explicitly so callers never need to
    read it back off builder instance state (see the concurrent-parsing
    investigation: a shared builder instance reused across concurrent
    parse() calls made a `self.last_structural_profile_inference`
    instance attribute an unsafe write-then-read-externally channel)."""

    payloads: list[ChunkPayload]
    structural_inference: StructuralProfileInference | None = None


__all__ = ["SectionChunkBuildResult"]
