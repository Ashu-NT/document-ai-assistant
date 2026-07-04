from typing import Protocol

from src.domain.extraction import (
    EquipmentInfo,
    ExtractionResult,
    MaintenanceTask,
    Manufacturer,
    SparePart,
    Supplier,
)


class ExtractionRepository(Protocol):
    def save_extraction_result(self, result: ExtractionResult) -> None:
        ...

    def replace_extraction_result(self, result: ExtractionResult) -> None:
        ...

    def delete_by_document(self, document_id: str) -> None:
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

    def list_manufacturers(
        self,
        document_id: str | None = None,
    ) -> list[Manufacturer]:
        ...

    def list_suppliers(
        self,
        document_id: str | None = None,
    ) -> list[Supplier]:
        ...

    def search_maintenance_tasks(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[MaintenanceTask]:
        ...

    def search_spare_parts(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[SparePart]:
        ...

    def search_equipment(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[EquipmentInfo]:
        ...

    def search_manufacturers(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Manufacturer]:
        ...

    def search_suppliers(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Supplier]:
        ...