from typing import Protocol

from src.domain.extraction import ExtractionResult, MaintenanceTask, SparePart, EquipmentInfo


class ExtractionRepository(Protocol):
    def save_extraction_result(self, result: ExtractionResult) -> None:
        ...

    def get_extraction_result(self, extraction_id: str) -> ExtractionResult | None:
        ...

    def list_maintenance_tasks(
        self,
        document_id: str | None = None,
    ) -> list[MaintenanceTask]:
        ...

    def list_spare_parts(
        self,
        document_id: str | None = None,
    ) -> list[SparePart]:
        ...

    def list_equipment(
        self,
        document_id: str | None = None,
    ) -> list[EquipmentInfo]:
        ...