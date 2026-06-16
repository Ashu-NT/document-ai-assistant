from typing import Protocol

from src.domain.document.entities import DocumentChunk
from src.domain.extraction import EquipmentInfo


class EquipmentExtractor(Protocol):
    def extract(self, chunks: list[DocumentChunk]) -> list[EquipmentInfo]:
        ...