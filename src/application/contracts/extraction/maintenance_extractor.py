from typing import Protocol

from src.domain.document.entities import DocumentChunk
from src.domain.extraction import MaintenanceTask


class MaintenanceExtractor(Protocol):
    def extract(self, chunks: list[DocumentChunk]) -> list[MaintenanceTask]:
        ...