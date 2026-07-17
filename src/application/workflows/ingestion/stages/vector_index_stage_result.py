from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.embedding import EmbeddedChunk


@dataclass(slots=True)
class VectorIndexStageResult:
    embedded_chunks: list[EmbeddedChunk]
    embedding_model: str | None
