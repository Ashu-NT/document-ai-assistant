from dataclasses import dataclass

from src.domain.document import DocumentChunk


@dataclass(slots=True, frozen=True)
class ExtractionBatch:
    batch_index: int
    batch_count: int
    chunks: list[DocumentChunk]
    char_count: int
    word_count: int

    @property
    def chunk_ids(self) -> list[str]:
        return [chunk.chunk_id for chunk in self.chunks]
