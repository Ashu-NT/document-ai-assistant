from dataclasses import dataclass, field
from enum import StrEnum

from src.domain.common import AuditMetadata
from src.domain.extraction.contact_point import ContactPoint
from src.domain.extraction.equipment_info import EquipmentInfo
from src.domain.extraction.extracted_identifier import ExtractedIdentifier
from src.domain.extraction.maintenance_interval import MaintenanceInterval
from src.domain.extraction.maintenance_task import MaintenanceTask
from src.domain.extraction.manufacturer import Manufacturer
from src.domain.extraction.procedure import Procedure
from src.domain.extraction.safety_warning import SafetyWarning
from src.domain.extraction.spare_part import SparePart
from src.domain.extraction.specification import Specification
from src.domain.extraction.supplier import Supplier
from src.domain.extraction.troubleshooting_entry import TroubleshootingEntry
from src.domain.extraction.unresolved_extraction_work import UnresolvedExtractionWork


class ExtractionCompletenessStatus(StrEnum):
    """Derived, read-only completeness state for one ExtractionResult.

    Deliberately never stored as its own field - always computed live from
    `attempted_chunk_ids`/`unresolved_chunk_ids` (see
    `ExtractionResult.completeness_status`) so it can never drift from, or
    contradict, those two lists. NOT inferred from entity counts: a
    document/scope can legitimately contain zero extractable entities and
    still be COMPLETE, and having some extracted entities does not imply
    COMPLETE if unresolved chunks remain.

    - COMPLETE: every requested chunk was either never attempted-and-failed
      or was successfully processed - `unresolved_chunk_ids` is empty.
    - PARTIAL: at least one requested chunk was successfully processed, but
      one or more requested chunks remain unresolved after retry/splitting.
      This is a legitimate resilient outcome, not an error.
    - FAILED: every chunk extraction was attempted on ended up unresolved -
      the requested extraction scope could not be successfully processed
      at all (not merely incompletely).
    """

    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(slots=True)
class ExtractionResult:
    extraction_id: str
    document_id: str

    maintenance_tasks: list[MaintenanceTask] = field(default_factory=list)
    spare_parts: list[SparePart] = field(default_factory=list)
    equipment: list[EquipmentInfo] = field(default_factory=list)
    manufacturers: list[Manufacturer] = field(default_factory=list)
    suppliers: list[Supplier] = field(default_factory=list)
    contact_points: list[ContactPoint] = field(default_factory=list)
    procedures: list[Procedure] = field(default_factory=list)
    specifications: list[Specification] = field(default_factory=list)
    safety_warnings: list[SafetyWarning] = field(default_factory=list)
    maintenance_intervals: list[MaintenanceInterval] = field(default_factory=list)
    troubleshooting_entries: list[TroubleshootingEntry] = field(default_factory=list)
    extracted_identifiers: list[ExtractedIdentifier] = field(default_factory=list)

    source_chunk_ids: list[str] = field(default_factory=list)
    attempted_chunk_ids: list[str] = field(default_factory=list)
    unresolved_chunk_ids: list[str] = field(default_factory=list)
    # Finer-grained (chunk, entity_type) unresolved records - only ever
    # populated under SPECIALIZED_FAMILY execution (see
    # UnresolvedExtractionWork's docstring). Always empty under MULTI_FAMILY,
    # and not yet persisted (no ORM column) - a deliberate, reported-not-
    # implemented follow-up, not an oversight.
    unresolved_extraction_work: list[UnresolvedExtractionWork] = field(
        default_factory=list
    )

    confidence_score: float | None = None
    requires_human_review: bool = True

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    @property
    def completeness_status(self) -> ExtractionCompletenessStatus:
        """Deterministic, derived from attempted_chunk_ids/unresolved_chunk_ids
        only - never from entity counts. See ExtractionCompletenessStatus's
        docstring for the exact invariant."""
        if not self.unresolved_chunk_ids:
            return ExtractionCompletenessStatus.COMPLETE
        resolved_chunk_ids = set(self.attempted_chunk_ids) - set(
            self.unresolved_chunk_ids
        )
        if resolved_chunk_ids:
            return ExtractionCompletenessStatus.PARTIAL
        return ExtractionCompletenessStatus.FAILED

    @property
    def is_complete(self) -> bool:
        return self.completeness_status is ExtractionCompletenessStatus.COMPLETE

    @property
    def is_partial(self) -> bool:
        return self.completeness_status is ExtractionCompletenessStatus.PARTIAL

    @property
    def is_failed(self) -> bool:
        return self.completeness_status is ExtractionCompletenessStatus.FAILED

    @property
    def has_unresolved_chunks(self) -> bool:
        return bool(self.unresolved_chunk_ids)

    def has_results(self) -> bool:
        return any(
            [
                self.maintenance_tasks,
                self.spare_parts,
                self.equipment,
                self.manufacturers,
                self.suppliers,
                self.contact_points,
                self.procedures,
                self.specifications,
                self.safety_warnings,
                self.maintenance_intervals,
                self.troubleshooting_entries,
                self.extracted_identifiers,
            ]
        )

    def task_count(self) -> int:
        return len(self.maintenance_tasks)

    def spare_part_count(self) -> int:
        return len(self.spare_parts)
