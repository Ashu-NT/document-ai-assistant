from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.builders.contact_point_builder import (
    ContactPointBuilder,
)
from src.application.workflows.extraction.builders.equipment_info_builder import (
    EquipmentInfoBuilder,
)
from src.application.workflows.extraction.builders.extracted_identifier_builder import (
    ExtractedIdentifierBuilder,
)
from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.builders.maintenance_interval_builder import (
    MaintenanceIntervalBuilder,
)
from src.application.workflows.extraction.builders.maintenance_task_builder import (
    MaintenanceTaskBuilder,
)
from src.application.workflows.extraction.builders.organization_entity_builder import (
    ManufacturerBuilder,
    SupplierBuilder,
)
from src.application.workflows.extraction.builders.procedure_builder import (
    ProcedureBuilder,
)
from src.application.workflows.extraction.builders.safety_warning_builder import (
    SafetyWarningBuilder,
)
from src.application.workflows.extraction.builders.specification_builder import (
    SpecificationBuilder,
)
from src.application.workflows.extraction.builders.spare_part_builder import (
    SparePartBuilder,
)
from src.application.workflows.extraction.builders.troubleshooting_entry_builder import (
    TroubleshootingEntryBuilder,
)
from src.application.workflows.extraction.response import ExtractionResponseParser
from src.domain.document import DocumentChunk
from src.domain.extraction import ExtractionResult
from src.shared.ids import IdGenerator, IdPrefix

# Assembles one batch's LLM response into a complete ExtractionResult:
# parses the response, then fans out each payload list to its per-entity
# builder, then aggregates the overall `requires_human_review` flag. Split
# out of extraction_workflow.py's `_build_extraction_result` -- the
# orchestrator (ExtractionWorkflow) now just calls `build()` once per
# batch attempt instead of implementing entity construction inline.


class ExtractionResultAssembler:
    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        response_parser: ExtractionResponseParser,
        support: ExtractionBuilderSupport,
    ) -> None:
        self._id_generator = id_generator
        self._response_parser = response_parser
        self._support = support
        self._maintenance_task_builder = MaintenanceTaskBuilder(id_generator, support)
        self._spare_part_builder = SparePartBuilder(id_generator, support)
        self._equipment_info_builder = EquipmentInfoBuilder(id_generator, support)
        self._manufacturer_builder = ManufacturerBuilder(id_generator, support)
        self._supplier_builder = SupplierBuilder(id_generator, support)
        self._contact_point_builder = ContactPointBuilder(id_generator, support)
        self._procedure_builder = ProcedureBuilder(id_generator, support)
        self._specification_builder = SpecificationBuilder(id_generator, support)
        self._safety_warning_builder = SafetyWarningBuilder(id_generator, support)
        self._maintenance_interval_builder = MaintenanceIntervalBuilder(id_generator, support)
        self._troubleshooting_entry_builder = TroubleshootingEntryBuilder(id_generator, support)
        self._extracted_identifier_builder = ExtractedIdentifierBuilder(support)

    @property
    def invalid_source_chunk_id_events(self) -> list[dict[str, Any]]:
        return self._support.invalid_source_chunk_id_events

    def build(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
        response: str,
    ) -> ExtractionResult:
        self._support.reset_invalid_source_chunk_id_events()
        payload = self._response_parser.parse(response)
        chunk_lookup = {chunk.chunk_id: chunk for chunk in chunks}
        default_source_chunk_id = chunks[0].chunk_id if len(chunks) == 1 else None
        overall_confidence = payload["confidence_score"]
        # payload was already filtered by ExtractionResponseSanitizer.sanitize()
        # inside self._response_parser.parse() above -- no need to re-filter here.
        maintenance_task_payloads = payload["maintenance_tasks"]
        spare_part_payloads = payload["spare_parts"]
        equipment_payloads = payload["equipment"]
        manufacturer_payloads = payload["manufacturers"]
        supplier_payloads = payload["suppliers"]
        contact_point_payloads = payload["contact_points"]
        procedure_payloads = payload["procedures"]
        specification_payloads = payload["specifications"]
        safety_warning_payloads = payload["safety_warnings"]
        maintenance_interval_payloads = payload["maintenance_intervals"]
        troubleshooting_entry_payloads = payload["troubleshooting_entries"]
        identifier_payloads = payload["identifiers"]

        maintenance_tasks = [
            self._maintenance_task_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in maintenance_task_payloads
        ]
        spare_parts = [
            self._spare_part_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in spare_part_payloads
        ]
        equipment = [
            self._equipment_info_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in equipment_payloads
        ]
        manufacturers = [
            self._manufacturer_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in manufacturer_payloads
        ]
        suppliers = [
            self._supplier_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in supplier_payloads
        ]
        contact_points = [
            self._contact_point_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in contact_point_payloads
        ]
        procedures = [
            self._procedure_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
                equipment=equipment,
            )
            for item in procedure_payloads
        ]
        specifications = [
            self._specification_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in specification_payloads
        ]
        safety_warnings = [
            self._safety_warning_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in safety_warning_payloads
        ]
        maintenance_intervals = [
            self._maintenance_interval_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
                maintenance_tasks=maintenance_tasks,
            )
            for item in maintenance_interval_payloads
        ]
        troubleshooting_entries = [
            self._troubleshooting_entry_builder.build(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
                equipment=equipment,
            )
            for item in troubleshooting_entry_payloads
        ]
        extracted_identifiers = [
            self._extracted_identifier_builder.build(
                item,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in identifier_payloads
        ]

        requires_human_review = self._support.resolve_requires_human_review(
            payload.get("requires_human_review"),
            overall_confidence,
        )
        requires_human_review = requires_human_review or any(
            item.requires_human_review
            for item in [
                *maintenance_tasks,
                *spare_parts,
                *equipment,
                *manufacturers,
                *suppliers,
                *contact_points,
                *procedures,
                *specifications,
                *safety_warnings,
                *maintenance_intervals,
                *troubleshooting_entries,
                *extracted_identifiers,
            ]
        )

        return ExtractionResult(
            extraction_id=self._id_generator.new_id(IdPrefix.EXTRACTION),
            document_id=document_id,
            maintenance_tasks=maintenance_tasks,
            spare_parts=spare_parts,
            equipment=equipment,
            manufacturers=manufacturers,
            suppliers=suppliers,
            contact_points=contact_points,
            procedures=procedures,
            specifications=specifications,
            safety_warnings=safety_warnings,
            maintenance_intervals=maintenance_intervals,
            troubleshooting_entries=troubleshooting_entries,
            extracted_identifiers=extracted_identifiers,
            source_chunk_ids=list(chunk_lookup),
            confidence_score=overall_confidence,
            requires_human_review=requires_human_review,
        )
