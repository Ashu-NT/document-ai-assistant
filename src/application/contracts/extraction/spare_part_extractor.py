from typing import Protocol

from src.domain.document.entities import DocumentChunk
from src.domain.extraction import SparePart


class SparePartExtractor(Protocol):
    def extract(self, chunks: list[DocumentChunk]) -> list[SparePart]:
        ...