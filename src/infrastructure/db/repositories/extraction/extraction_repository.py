from sqlalchemy.orm import Session

from src.application.contracts.extraction import ExtractionRepository
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
from src.infrastructure.db.repositories.extraction.equipment_reader import EquipmentReader
from src.infrastructure.db.repositories.extraction.extraction_reader import ExtractionReader
from src.infrastructure.db.repositories.extraction.extraction_writer import ExtractionWriter
from src.infrastructure.db.repositories.extraction.maintenance_interval_reader import (
    MaintenanceIntervalReader,
)
from src.infrastructure.db.repositories.extraction.maintenance_task_reader import (
    MaintenanceTaskReader,
)
from src.infrastructure.db.repositories.extraction.manufacturer_reader import (
    ManufacturerReader,
)
from src.infrastructure.db.repositories.extraction.procedure_reader import ProcedureReader
from src.infrastructure.db.repositories.extraction.safety_warning_reader import (
    SafetyWarningReader,
)
from src.infrastructure.db.repositories.extraction.spare_part_reader import SparePartReader
from src.infrastructure.db.repositories.extraction.specification_reader import (
    SpecificationReader,
)
from src.infrastructure.db.repositories.extraction.supplier_reader import SupplierReader
from src.infrastructure.db.repositories.extraction.troubleshooting_entry_reader import (
    TroubleshootingEntryReader,
)


class SqlAlchemyExtractionRepository(ExtractionRepository):
    def __init__(self, session: Session) -> None:
        self.writer = ExtractionWriter(session)
        self.reader = ExtractionReader(session)
        self.task_reader = MaintenanceTaskReader(session)
        self.spare_part_reader = SparePartReader(session)
        self.equipment_reader = EquipmentReader(session)
        self.manufacturer_reader = ManufacturerReader(session)
        self.supplier_reader = SupplierReader(session)
        self.procedure_reader = ProcedureReader(session)
        self.specification_reader = SpecificationReader(session)
        self.safety_warning_reader = SafetyWarningReader(session)
        self.maintenance_interval_reader = MaintenanceIntervalReader(session)
        self.troubleshooting_entry_reader = TroubleshootingEntryReader(session)

    def save_extraction_result(self, result: ExtractionResult) -> None:
        self.writer.save_extraction_result(result)

    def replace_extraction_result(self, result: ExtractionResult) -> None:
        self.writer.replace_extraction_result(result)

    def delete_by_document(self, document_id: str) -> None:
        self.writer.delete_by_document(document_id)

    def get_extraction_result(
        self,
        extraction_id: str,
    ) -> ExtractionResult | None:
        return self.reader.get_extraction_result(extraction_id)

    def list_maintenance_tasks(
        self,
        document_id: str | None = None,
    ) -> list[MaintenanceTask]:
        return self.task_reader.list_maintenance_tasks(document_id)

    def list_spare_parts(
        self,
        document_id: str | None = None,
    ) -> list[SparePart]:
        return self.spare_part_reader.list_spare_parts(document_id)

    def list_equipment(
        self,
        document_id: str | None = None,
    ) -> list[EquipmentInfo]:
        return self.equipment_reader.list_equipment(document_id)

    def list_manufacturers(
        self,
        document_id: str | None = None,
    ) -> list[Manufacturer]:
        return self.manufacturer_reader.list_manufacturers(document_id)

    def list_suppliers(
        self,
        document_id: str | None = None,
    ) -> list[Supplier]:
        return self.supplier_reader.list_suppliers(document_id)

    def list_procedures(
        self,
        document_id: str | None = None,
    ) -> list[Procedure]:
        return self.procedure_reader.list_procedures(document_id)

    def list_specifications(
        self,
        document_id: str | None = None,
    ) -> list[Specification]:
        return self.specification_reader.list_specifications(document_id)

    def list_safety_warnings(
        self,
        document_id: str | None = None,
    ) -> list[SafetyWarning]:
        return self.safety_warning_reader.list_safety_warnings(document_id)

    def list_maintenance_intervals(
        self,
        document_id: str | None = None,
    ) -> list[MaintenanceInterval]:
        return self.maintenance_interval_reader.list_maintenance_intervals(document_id)

    def list_troubleshooting_entries(
        self,
        document_id: str | None = None,
    ) -> list[TroubleshootingEntry]:
        return self.troubleshooting_entry_reader.list_troubleshooting_entries(document_id)

    def search_maintenance_tasks(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[MaintenanceTask]:
        return self.task_reader.search_maintenance_tasks(query, document_id)

    def search_spare_parts(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[SparePart]:
        return self.spare_part_reader.search_spare_parts(query, document_id)

    def search_equipment(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[EquipmentInfo]:
        return self.equipment_reader.search_equipment(query, document_id)

    def search_manufacturers(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Manufacturer]:
        return self.manufacturer_reader.search_manufacturers(query, document_id)

    def search_suppliers(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Supplier]:
        return self.supplier_reader.search_suppliers(query, document_id)

    def search_procedures(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Procedure]:
        return self.procedure_reader.search_procedures(query, document_id)

    def search_specifications(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Specification]:
        return self.specification_reader.search_specifications(query, document_id)

    def search_safety_warnings(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[SafetyWarning]:
        return self.safety_warning_reader.search_safety_warnings(query, document_id)

    def search_maintenance_intervals(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[MaintenanceInterval]:
        return self.maintenance_interval_reader.search_maintenance_intervals(
            query, document_id
        )

    def search_troubleshooting_entries(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[TroubleshootingEntry]:
        return self.troubleshooting_entry_reader.search_troubleshooting_entries(
            query, document_id
        )

    def list_maintenance_intervals_by_task_id(
        self,
        maintenance_task_id: str,
    ) -> list[MaintenanceInterval]:
        return self.maintenance_interval_reader.list_by_maintenance_task_id(
            maintenance_task_id
        )

    def list_procedures_by_equipment_id(
        self,
        equipment_id: str,
    ) -> list[Procedure]:
        return self.procedure_reader.list_by_equipment_id(equipment_id)

    def list_troubleshooting_entries_by_equipment_id(
        self,
        equipment_id: str,
    ) -> list[TroubleshootingEntry]:
        return self.troubleshooting_entry_reader.list_by_equipment_id(equipment_id)
