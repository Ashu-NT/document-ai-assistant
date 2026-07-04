from dataclasses import dataclass, field
from enum import StrEnum

from src.domain.common import AuditMetadata, SourceLocation


class ProcedureType(StrEnum):
    MAINTENANCE = "maintenance"
    INSPECTION = "inspection"
    REPLACEMENT = "replacement"
    REPAIR = "repair"
    INSTALLATION = "installation"
    COMMISSIONING = "commissioning"
    OPERATION = "operation"
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    CALIBRATION = "calibration"
    TESTING = "testing"
    TROUBLESHOOTING = "troubleshooting"
    SAFETY = "safety"
    CLEANING_FLUSHING = "cleaning_flushing"
    ASSEMBLY_DISASSEMBLY = "assembly_disassembly"
    STORAGE_PRESERVATION = "storage_preservation"
    DECOMMISSIONING = "decommissioning"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class Procedure:
    procedure_id: str
    document_id: str

    title: str
    procedure_type: ProcedureType = ProcedureType.UNKNOWN
    steps: list[str] = field(default_factory=list)
    component_name: str | None = None
    equipment_id: str | None = None

    source_chunk_id: str | None = None
    source: SourceLocation = field(default_factory=SourceLocation)

    confidence_score: float | None = None
    requires_human_review: bool = True

    audit: AuditMetadata = field(default_factory=AuditMetadata)
