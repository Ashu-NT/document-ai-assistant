from dataclasses import dataclass, field

from src.domain.common import AuditMetadata
from src.domain.extraction.equipment_info import EquipmentInfo
from src.domain.extraction.extracted_identifier import ExtractedIdentifier
from src.domain.extraction.maintenance_task import MaintenanceTask
from src.domain.extraction.manufacturer import Manufacturer
from src.domain.extraction.spare_part import SparePart


@dataclass(slots=True)
class ExtractionResult:
    extraction_id: str
    document_id: str

    maintenance_tasks: list[MaintenanceTask] = field(default_factory=list)
    spare_parts: list[SparePart] = field(default_factory=list)
    equipment: list[EquipmentInfo] = field(default_factory=list)
    manufacturers: list[Manufacturer] = field(default_factory=list)
    extracted_identifiers: list[ExtractedIdentifier] = field(default_factory=list)

    source_chunk_ids: list[str] = field(default_factory=list)

    confidence_score: float | None = None
    requires_human_review: bool = True

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_results(self) -> bool:
        return any(
            [
                self.maintenance_tasks,
                self.spare_parts,
                self.equipment,
                self.manufacturers,
                self.extracted_identifiers,
            ]
        )

    def task_count(self) -> int:
        return len(self.maintenance_tasks)

    def spare_part_count(self) -> int:
        return len(self.spare_parts)