from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)


@dataclass(slots=True, frozen=True)
class ChunkPayloadDeduplicationResult:
    payloads: list[ChunkPayload]
    diagnostics: list[dict[str, object]] = field(default_factory=list)

