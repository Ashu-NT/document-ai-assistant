from src.domain.common import SourceLocation
from src.domain.extraction import (
    EquipmentInfo,
    ExtractedIdentifier,
    ExtractionResult,
    MaintenanceInterval,
    MaintenanceTask,
    Manufacturer,
    Procedure,
    ProcedureType,
    SafetyWarning,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
)
from src.shared.ids import IdGenerator, IdPrefix


class ExtractionResultMerger:
    def __init__(self, *, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def merge(
        self,
        *,
        document_id: str,
        partial_results: list[ExtractionResult],
    ) -> ExtractionResult:
        merged_tasks = self._merge_tasks(partial_results)
        merged_parts = self._merge_spare_parts(partial_results)
        merged_equipment = self._merge_equipment(partial_results)
        merged_manufacturers = self._merge_manufacturers(partial_results)
        merged_suppliers = self._merge_suppliers(partial_results)
        merged_procedures = self._merge_procedures(partial_results)
        merged_specifications = self._merge_specifications(partial_results)
        merged_safety_warnings = self._merge_safety_warnings(partial_results)
        merged_maintenance_intervals = self._merge_maintenance_intervals(partial_results)
        merged_troubleshooting_entries = self._merge_troubleshooting_entries(partial_results)
        merged_identifiers = self._merge_identifiers(partial_results)
        source_chunk_ids = self._unique_in_order(
            chunk_id
            for result in partial_results
            for chunk_id in result.source_chunk_ids
        )
        confidences = [
            result.confidence_score
            for result in partial_results
            if result.confidence_score is not None
        ]
        confidence_score = (
            sum(confidences) / len(confidences)
            if confidences
            else 0.0
        )

        return ExtractionResult(
            extraction_id=self.id_generator.new_id(IdPrefix.EXTRACTION),
            document_id=document_id,
            maintenance_tasks=merged_tasks,
            spare_parts=merged_parts,
            equipment=merged_equipment,
            manufacturers=merged_manufacturers,
            suppliers=merged_suppliers,
            procedures=merged_procedures,
            specifications=merged_specifications,
            safety_warnings=merged_safety_warnings,
            maintenance_intervals=merged_maintenance_intervals,
            troubleshooting_entries=merged_troubleshooting_entries,
            extracted_identifiers=merged_identifiers,
            source_chunk_ids=source_chunk_ids,
            confidence_score=confidence_score,
            requires_human_review=any(
                result.requires_human_review
                for result in partial_results
            ),
        )

    def _merge_tasks(self, partial_results: list[ExtractionResult]) -> list[MaintenanceTask]:
        merged: dict[tuple[str, ...], MaintenanceTask] = {}
        for result in partial_results:
            for item in result.maintenance_tasks:
                key = (
                    self._normalize(item.title),
                    self._normalize(item.interval),
                    self._normalize(item.component_name or item.equipment_id),
                )
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_task(merged[key], item)
        return list(merged.values())

    def _merge_spare_parts(self, partial_results: list[ExtractionResult]) -> list[SparePart]:
        merged: dict[tuple[str, ...], SparePart] = {}
        for result in partial_results:
            for item in result.spare_parts:
                key = (
                    self._normalize(item.part_number or item.description),
                    self._normalize(item.manufacturer_name),
                    self._normalize(item.component_name),
                )
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_spare_part(merged[key], item)
        return list(merged.values())

    def _merge_equipment(self, partial_results: list[ExtractionResult]) -> list[EquipmentInfo]:
        merged: dict[tuple[str, ...], EquipmentInfo] = {}
        for result in partial_results:
            for item in result.equipment:
                key = (
                    self._normalize(item.name),
                    self._normalize(item.model_number),
                    self._normalize(item.serial_number),
                    self._normalize(item.manufacturer_name),
                )
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_equipment_info(merged[key], item)
        return list(merged.values())

    def _merge_manufacturers(self, partial_results: list[ExtractionResult]) -> list[Manufacturer]:
        merged: dict[str, Manufacturer] = {}
        for result in partial_results:
            for item in result.manufacturers:
                key = self._normalize(item.name)
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_manufacturer(merged[key], item)
        return list(merged.values())

    def _merge_suppliers(self, partial_results: list[ExtractionResult]) -> list[Supplier]:
        merged: dict[str, Supplier] = {}
        for result in partial_results:
            for item in result.suppliers:
                key = self._normalize(item.name)
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_supplier(merged[key], item)
        return list(merged.values())

    def _merge_procedures(self, partial_results: list[ExtractionResult]) -> list[Procedure]:
        merged: dict[tuple[str, ...], Procedure] = {}
        for result in partial_results:
            for item in result.procedures:
                key = (
                    self._normalize(item.title),
                    self._normalize(item.component_name),
                )
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_procedure(merged[key], item)
        return list(merged.values())

    def _merge_specifications(
        self,
        partial_results: list[ExtractionResult],
    ) -> list[Specification]:
        merged: dict[tuple[str, ...], Specification] = {}
        for result in partial_results:
            for item in result.specifications:
                key = (
                    self._normalize(item.parameter),
                    self._normalize(item.component_name),
                )
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_specification(merged[key], item)
        return list(merged.values())

    def _merge_safety_warnings(
        self,
        partial_results: list[ExtractionResult],
    ) -> list[SafetyWarning]:
        merged: dict[str, SafetyWarning] = {}
        for result in partial_results:
            for item in result.safety_warnings:
                key = self._normalize(item.message)
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_safety_warning(merged[key], item)
        return list(merged.values())

    def _merge_maintenance_intervals(
        self,
        partial_results: list[ExtractionResult],
    ) -> list[MaintenanceInterval]:
        merged: dict[tuple[str, ...], MaintenanceInterval] = {}
        for result in partial_results:
            for item in result.maintenance_intervals:
                key = (
                    self._normalize(item.interval),
                    self._normalize(item.component_name),
                )
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_maintenance_interval(merged[key], item)
        return list(merged.values())

    def _merge_troubleshooting_entries(
        self,
        partial_results: list[ExtractionResult],
    ) -> list[TroubleshootingEntry]:
        merged: dict[tuple[str, ...], TroubleshootingEntry] = {}
        for result in partial_results:
            for item in result.troubleshooting_entries:
                key = (
                    self._normalize(item.symptom),
                    self._normalize(item.component_name),
                )
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_troubleshooting_entry(merged[key], item)
        return list(merged.values())

    def _merge_identifiers(
        self,
        partial_results: list[ExtractionResult],
    ) -> list[ExtractedIdentifier]:
        merged: dict[tuple[str, str], ExtractedIdentifier] = {}
        for result in partial_results:
            for item in result.extracted_identifiers:
                key = (
                    self._normalize(item.raw_value),
                    self._normalize(item.identifier_type),
                )
                if key not in merged:
                    merged[key] = item
                    continue
                self._merge_identifier(merged[key], item)
        return list(merged.values())

    def _merge_task(self, current: MaintenanceTask, candidate: MaintenanceTask) -> None:
        current.description = current.description or candidate.description
        current.interval = current.interval or candidate.interval
        current.component_name = current.component_name or candidate.component_name
        current.equipment_id = current.equipment_id or candidate.equipment_id
        self._merge_common_fields(current, candidate)

    def _merge_spare_part(self, current: SparePart, candidate: SparePart) -> None:
        current.part_number = current.part_number or candidate.part_number
        current.description = current.description or candidate.description
        current.quantity = current.quantity or candidate.quantity
        current.component_name = current.component_name or candidate.component_name
        current.manufacturer_name = current.manufacturer_name or candidate.manufacturer_name
        self._merge_common_fields(current, candidate)

    def _merge_equipment_info(self, current: EquipmentInfo, candidate: EquipmentInfo) -> None:
        current.name = current.name or candidate.name
        current.model_number = current.model_number or candidate.model_number
        current.serial_number = current.serial_number or candidate.serial_number
        current.manufacturer_name = current.manufacturer_name or candidate.manufacturer_name
        self._merge_common_fields(current, candidate)

    def _merge_manufacturer(self, current: Manufacturer, candidate: Manufacturer) -> None:
        current.website = current.website or candidate.website
        current.country = current.country or candidate.country
        self._merge_common_fields(current, candidate)

    def _merge_supplier(self, current: Supplier, candidate: Supplier) -> None:
        current.website = current.website or candidate.website
        current.country = current.country or candidate.country
        self._merge_common_fields(current, candidate)

    def _merge_procedure(self, current: Procedure, candidate: Procedure) -> None:
        current.steps = current.steps or candidate.steps
        current.component_name = current.component_name or candidate.component_name
        current.equipment_id = current.equipment_id or candidate.equipment_id
        if current.procedure_type == ProcedureType.UNKNOWN:
            current.procedure_type = candidate.procedure_type
        self._merge_common_fields(current, candidate)

    def _merge_specification(self, current: Specification, candidate: Specification) -> None:
        current.unit = current.unit or candidate.unit
        current.component_name = current.component_name or candidate.component_name
        self._merge_common_fields(current, candidate)

    def _merge_safety_warning(self, current: SafetyWarning, candidate: SafetyWarning) -> None:
        current.component_name = current.component_name or candidate.component_name
        self._merge_common_fields(current, candidate)

    def _merge_maintenance_interval(
        self,
        current: MaintenanceInterval,
        candidate: MaintenanceInterval,
    ) -> None:
        current.maintenance_task_id = (
            current.maintenance_task_id or candidate.maintenance_task_id
        )
        self._merge_common_fields(current, candidate)

    def _merge_troubleshooting_entry(
        self,
        current: TroubleshootingEntry,
        candidate: TroubleshootingEntry,
    ) -> None:
        current.cause = current.cause or candidate.cause
        current.remedy = current.remedy or candidate.remedy
        current.component_name = current.component_name or candidate.component_name
        current.equipment_id = current.equipment_id or candidate.equipment_id
        self._merge_common_fields(current, candidate)

    def _merge_identifier(
        self,
        current: ExtractedIdentifier,
        candidate: ExtractedIdentifier,
    ) -> None:
        current.source_chunk_id = current.source_chunk_id or candidate.source_chunk_id
        current.confidence_score = self._best_confidence(
            current.confidence_score,
            candidate.confidence_score,
        )
        current.requires_human_review = (
            current.requires_human_review
            or candidate.requires_human_review
        )

    def _merge_common_fields(self, current, candidate) -> None:
        current.source_chunk_id = current.source_chunk_id or candidate.source_chunk_id
        current.confidence_score = self._best_confidence(
            current.confidence_score,
            candidate.confidence_score,
        )
        current.requires_human_review = (
            current.requires_human_review
            or candidate.requires_human_review
        )
        if self._is_empty_source(current.source) and not self._is_empty_source(candidate.source):
            current.source = SourceLocation(
                page_start=candidate.source.page_start,
                page_end=candidate.source.page_end,
                bbox=candidate.source.bbox,
            )

    @staticmethod
    def _best_confidence(
        left: float | None,
        right: float | None,
    ) -> float | None:
        if left is None:
            return right
        if right is None:
            return left
        return max(left, right)

    @staticmethod
    def _is_empty_source(source: SourceLocation) -> bool:
        return source.page_start is None and source.page_end is None and source.bbox is None

    @staticmethod
    def _normalize(value: str | None) -> str:
        if value is None:
            return ""
        normalized = "".join(
            character.lower()
            for character in value.strip()
            if character.isalnum()
        )
        return normalized

    @staticmethod
    def _unique_in_order(values) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            ordered.append(value)
        return ordered
