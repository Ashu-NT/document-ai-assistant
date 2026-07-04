from sqlalchemy.orm import Session

from src.application.contracts.extraction import ExtractionRepository
from src.domain.extraction import (
    EquipmentInfo,
    ExtractionResult,
    MaintenanceTask,
    Manufacturer,
    SparePart,
    Supplier,
)
from src.infrastructure.db.repositories.extraction.equipment_reader import EquipmentReader
from src.infrastructure.db.repositories.extraction.extraction_reader import ExtractionReader
from src.infrastructure.db.repositories.extraction.extraction_writer import ExtractionWriter
from src.infrastructure.db.repositories.extraction.maintenance_task_reader import (
    MaintenanceTaskReader,
)
from src.infrastructure.db.repositories.extraction.manufacturer_reader import (
    ManufacturerReader,
)
from src.infrastructure.db.repositories.extraction.spare_part_reader import SparePartReader
from src.infrastructure.db.repositories.extraction.supplier_reader import SupplierReader


class SqlAlchemyExtractionRepository(ExtractionRepository):
    def __init__(self, session: Session) -> None:
        self.writer = ExtractionWriter(session)
        self.reader = ExtractionReader(session)
        self.task_reader = MaintenanceTaskReader(session)
        self.spare_part_reader = SparePartReader(session)
        self.equipment_reader = EquipmentReader(session)
        self.manufacturer_reader = ManufacturerReader(session)
        self.supplier_reader = SupplierReader(session)

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