from typing import Protocol

from src.domain.extraction import (
    EquipmentInfo,
    ExtractionResult,
    MaintenanceInterval,
    MaintenanceTask,
    Manufacturer,
    Procedure,
    SafetyWarning,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
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

    def list_procedures(
        self,
        document_id: str | None = None,
    ) -> list[Procedure]:
        ...

    def list_specifications(
        self,
        document_id: str | None = None,
    ) -> list[Specification]:
        ...

    def list_safety_warnings(
        self,
        document_id: str | None = None,
    ) -> list[SafetyWarning]:
        ...

    def list_maintenance_intervals(
        self,
        document_id: str | None = None,
    ) -> list[MaintenanceInterval]:
        ...

    def list_troubleshooting_entries(
        self,
        document_id: str | None = None,
    ) -> list[TroubleshootingEntry]:
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

    def search_procedures(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Procedure]:
        ...

    def search_specifications(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Specification]:
        ...

    def search_safety_warnings(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[SafetyWarning]:
        ...

    def search_maintenance_intervals(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[MaintenanceInterval]:
        ...

    def search_troubleshooting_entries(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[TroubleshootingEntry]:
        ...

    def list_maintenance_intervals_by_task_id(
        self,
        maintenance_task_id: str,
    ) -> list[MaintenanceInterval]:
        ...

    def list_procedures_by_equipment_id(
        self,
        equipment_id: str,
    ) -> list[Procedure]:
        ...

    def list_troubleshooting_entries_by_equipment_id(
        self,
        equipment_id: str,
    ) -> list[TroubleshootingEntry]:
        ...
