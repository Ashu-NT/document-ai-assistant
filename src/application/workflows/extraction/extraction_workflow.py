import re
from dataclasses import replace as dataclass_replace
from typing import Any
from collections.abc import Callable

from src.application.prompts.extraction import IdentifierExtractionPromptBuilder
from src.application.services.ai import LLMService
from src.application.services.extraction import ExtractionService
from src.application.validation.common import ValidationResult
from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.extraction.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.extraction_batch_diagnostics import (
    ExtractionBatchDiagnostics,
    safe_response_preview,
)
from src.application.workflows.extraction.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
from src.application.workflows.extraction.extraction_result_merger import (
    ExtractionResultMerger,
)
from src.application.workflows.extraction.extraction_response_parser import (
    ExtractionResponseParser,
)
from src.application.workflows.extraction.extraction_response_schema import (
    build_extraction_response_json_schema,
)
from src.domain.assets import TableAsset
from src.domain.common import SourceLocation
from src.domain.document import DocumentChunk
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
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator, IdPrefix

KEY_PATTERN = re.compile(r"[^a-z0-9]+")
NULL_LIKE_TEXT_VALUES = {
    "",
    "null",
    "none",
    "n/a",
    "na",
    "not available",
    "not applicable",
    "-",
    "--",
}


def _default_extraction_model() -> str | None:
    try:
        from src.config.settings import llm_settings

        return llm_settings.extraction_llm or llm_settings.general_llm
    except Exception:
        return None


def _default_extraction_confidence_threshold() -> float:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_confidence_threshold
    except Exception:
        return 1.0


def _default_extraction_require_human_review() -> bool:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_require_human_review
    except Exception:
        return True


def _default_max_chunks_per_batch() -> int:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_chunks_per_batch
    except Exception:
        return 16


def _default_max_chars_per_batch() -> int:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_chars_per_batch
    except Exception:
        return 16_000


def _default_allow_partial_batches() -> bool:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_allow_partial_batches
    except Exception:
        return False


def _default_failure_preview_chars() -> int:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_failure_preview_chars
    except Exception:
        return 1_200


def _default_extraction_max_attempts() -> int:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_attempts
    except Exception:
        return 2


def _default_extraction_temperature() -> float:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_temperature
    except Exception:
        return 0.0


def _default_extraction_json_mode() -> bool:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_json_mode
    except Exception:
        return True


class ExtractionWorkflow:
    def __init__(
        self,
        llm_service: LLMService,
        extraction_service: ExtractionService,
        extraction_result_validator: ExtractionResultValidator,
        id_generator: IdGenerator,
        prompt_builder: IdentifierExtractionPromptBuilder | None = None,
        response_parser: ExtractionResponseParser | None = None,
        extraction_model: str | None = None,
        confidence_threshold: float | None = None,
        require_human_review_default: bool | None = None,
        chunk_batcher: ExtractionChunkBatcher | None = None,
        result_merger: ExtractionResultMerger | None = None,
        allow_partial_batches: bool | None = None,
        failure_preview_chars: int | None = None,
        max_attempts: int | None = None,
        temperature: float | None = None,
        json_mode: bool | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.extraction_service = extraction_service
        self.extraction_result_validator = extraction_result_validator
        self.id_generator = id_generator
        self.prompt_builder = prompt_builder or IdentifierExtractionPromptBuilder()
        self.response_parser = response_parser or ExtractionResponseParser()
        self.extraction_model = extraction_model or _default_extraction_model()
        self.confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else _default_extraction_confidence_threshold()
        )
        self.require_human_review_default = (
            require_human_review_default
            if require_human_review_default is not None
            else _default_extraction_require_human_review()
        )
        self.chunk_batcher = chunk_batcher or ExtractionChunkBatcher(
            max_chunks_per_batch=_default_max_chunks_per_batch(),
            max_chars_per_batch=_default_max_chars_per_batch(),
        )
        self.result_merger = result_merger or ExtractionResultMerger(
            id_generator=id_generator
        )
        self.allow_partial_batches = (
            allow_partial_batches
            if allow_partial_batches is not None
            else _default_allow_partial_batches()
        )
        self.failure_preview_chars = (
            failure_preview_chars
            if failure_preview_chars is not None
            else _default_failure_preview_chars()
        )
        self.max_attempts = max(
            1,
            max_attempts
            if max_attempts is not None
            else _default_extraction_max_attempts(),
        )
        self.temperature = (
            temperature
            if temperature is not None
            else _default_extraction_temperature()
        )
        self.json_mode = (
            json_mode
            if json_mode is not None
            else _default_extraction_json_mode()
        )
        self.last_batch_diagnostics: list[ExtractionBatchDiagnostics] = []
        self._invalid_source_chunk_id_events: list[dict[str, Any]] = []

    @tracked_action(
        action="extraction.generated",
        entity_type="document",
        activity=True,
        audit=False,
        event=False,
    )
    def extract(
        self,
        document_id: str,
        chunks: DocumentChunk | list[DocumentChunk],
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
        replace_existing: bool = False,
        tables: dict[str, TableAsset] | None = None,
    ) -> ExtractionResult:
        chunk_list = self._coerce_chunks(chunks)
        self._emit_progress(
            progress_callback,
            f"Preparing extraction input from {len(chunk_list)} final chunk(s)...",
        )
        self._validate_input(document_id, chunk_list)
        self.last_batch_diagnostics = []

        if tables:
            chunk_list = self._hydrate_table_chunks(chunk_list, tables)

        batches = self.chunk_batcher.build_batches(chunk_list)
        self._emit_progress(
            progress_callback,
            f"Prepared {len(batches)} extraction batch(es).",
        )
        partial_results: list[ExtractionResult] = []
        unresolved_batches: list[ExtractionBatch] = []
        for batch in batches:
            partial_result = self._extract_batch_with_retries(
                document_id=document_id,
                batch=batch,
                activity_context=activity_context,
                progress_callback=progress_callback,
            )
            if partial_result is not None:
                partial_results.append(partial_result)
            else:
                unresolved_batches.append(batch)

        if not partial_results:
            raise SchemaValidationError(
                "Extraction produced no valid batch results.",
                details={
                    "document_id": document_id,
                    "batch_count": len(batches),
                    "diagnostics": [
                        diagnostic.to_dict()
                        for diagnostic in self.last_batch_diagnostics
                    ],
                },
            )

        if unresolved_batches:
            self._emit_progress(
                progress_callback,
                (
                    f"Extraction completed with {len(unresolved_batches)} of "
                    f"{len(batches)} batch(es) skipped after exhausting retries: "
                    f"{[batch.batch_index for batch in unresolved_batches]}."
                ),
            )

        extraction_result = self.result_merger.merge(
            document_id=document_id,
            partial_results=partial_results,
        )
        extraction_result.requires_human_review = (
            self._resolve_requires_human_review(
                None,
                extraction_result.confidence_score,
            )
            or extraction_result.requires_human_review
            or bool(unresolved_batches)
            or any(
                item.requires_human_review
                for item in [
                    *extraction_result.maintenance_tasks,
                    *extraction_result.spare_parts,
                    *extraction_result.equipment,
                    *extraction_result.manufacturers,
                    *extraction_result.extracted_identifiers,
                ]
            )
        )

        self._emit_progress(
            progress_callback,
            "Validating extraction result...",
        )
        validation = self.extraction_result_validator.validate(extraction_result)
        validation.raise_if_invalid()

        self._emit_progress(
            progress_callback,
            "Replacing extraction result..." if replace_existing else "Saving extraction result...",
        )
        if replace_existing:
            self.extraction_service.replace_extraction_result(
                extraction_result,
                activity_context=activity_context,
            )
        else:
            self.extraction_service.save_extraction_result(
                extraction_result,
                activity_context=activity_context,
            )
        self._emit_progress(
            progress_callback,
            (
                "Extraction completed "
                f"(maintenance_tasks={len(extraction_result.maintenance_tasks)}, "
                f"spare_parts={len(extraction_result.spare_parts)}, "
                f"equipment={len(extraction_result.equipment)}, "
                f"manufacturers={len(extraction_result.manufacturers)}, "
                f"suppliers={len(extraction_result.suppliers)}, "
                f"procedures={len(extraction_result.procedures)}, "
                f"specifications={len(extraction_result.specifications)}, "
                f"safety_warnings={len(extraction_result.safety_warnings)}, "
                f"maintenance_intervals={len(extraction_result.maintenance_intervals)}, "
                f"troubleshooting_entries={len(extraction_result.troubleshooting_entries)}, "
                f"identifiers={len(extraction_result.extracted_identifiers)}, "
                f"batches={len(batches)})."
            ),
        )
        return extraction_result

    def _extract_batch_with_retries(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
    ) -> ExtractionResult | None:
        last_exc: SchemaValidationError | None = None
        for attempt_index in range(1, self.max_attempts + 1):
            try:
                return self._extract_batch_once(
                    document_id=document_id,
                    batch=batch,
                    activity_context=activity_context,
                    progress_callback=progress_callback,
                    previous_error=(
                        self._describe_error_for_feedback(last_exc)
                        if last_exc is not None
                        else None
                    ),
                )
            except SchemaValidationError as exc:
                last_exc = exc
                if attempt_index < self.max_attempts:
                    self._emit_progress(
                        progress_callback,
                        (
                            f"[extraction {batch.batch_index}/{batch.batch_count}] "
                            f"attempt {attempt_index}/{self.max_attempts} failed "
                            f"schema parsing: {exc}. Retrying this batch only..."
                        ),
                    )

        if self.allow_partial_batches:
            self._emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"failed after {self.max_attempts} attempt(s); marking batch "
                    "extraction_failed and continuing with the remaining batches."
                ),
            )
            return None

        assert last_exc is not None
        raise last_exc

    @staticmethod
    def _describe_error_for_feedback(exc: SchemaValidationError) -> str:
        parse_error = exc.details.get("parse_error")
        return parse_error if isinstance(parse_error, str) else str(exc)

    def _extract_batch_once(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        previous_error: str | None = None,
    ) -> ExtractionResult:
        self._emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] "
                f"Building extraction prompt from {len(batch.chunks)} chunk(s) "
                f"({batch.char_count} chars, {batch.word_count} words)..."
            ),
        )
        prompt = self.prompt_builder.build(
            document_id,
            batch.chunks,
            previous_error=previous_error,
        )
        self._emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] "
                f"Calling extraction model {self.extraction_model or 'default'}..."
            ),
        )
        response = self.llm_service.generate(
            prompt,
            model=self.extraction_model,
            activity_context=activity_context,
            temperature=self.temperature,
            json_mode=self.json_mode,
            response_schema=build_extraction_response_json_schema(),
        )
        self._emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] "
                "Extraction model response received. Parsing structured payload..."
            ),
        )
        try:
            extraction_result = self._build_extraction_result(
                document_id,
                batch.chunks,
                response,
            )
        except SchemaValidationError as exc:
            preview = safe_response_preview(
                response,
                max_chars=self.failure_preview_chars,
            )
            diagnostics = ExtractionBatchDiagnostics(
                batch_index=batch.batch_index,
                batch_count=batch.batch_count,
                chunk_ids=batch.chunk_ids,
                char_count=batch.char_count,
                word_count=batch.word_count,
                model_name=self.extraction_model,
                parse_success=False,
                parse_error=str(exc),
                raw_response_preview=preview,
            )
            self.last_batch_diagnostics.append(diagnostics)
            compact_preview = " ".join(preview.split())
            self._emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"Schema parsing failed: {exc}. "
                    f"Response preview: {compact_preview}"
                ),
            )
            raise SchemaValidationError(
                f"Extraction batch {batch.batch_index}/{batch.batch_count} failed schema parsing.",
                details=diagnostics.to_dict(),
            ) from exc

        if self._invalid_source_chunk_id_events:
            event_count = len(self._invalid_source_chunk_id_events)
            self._emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"{event_count} item(s) referenced a source_chunk_id outside "
                    "this batch; flagged for human review and pinned to a "
                    "fallback chunk instead of failing the batch."
                ),
            )

        self.last_batch_diagnostics.append(
            ExtractionBatchDiagnostics(
                batch_index=batch.batch_index,
                batch_count=batch.batch_count,
                chunk_ids=batch.chunk_ids,
                char_count=batch.char_count,
                word_count=batch.word_count,
                model_name=self.extraction_model,
                parse_success=True,
            )
        )
        return extraction_result

    @staticmethod
    def _coerce_chunks(
        chunks: DocumentChunk | list[DocumentChunk],
    ) -> list[DocumentChunk]:
        if isinstance(chunks, list):
            return chunks

        return [chunks]

    @staticmethod
    def _hydrate_table_chunks(
        chunks: list[DocumentChunk],
        tables: dict[str, TableAsset],
    ) -> list[DocumentChunk]:
        """Replaces a chunk's (possibly partial) content with the complete
        table markdown whenever the chunk references a table.

        The chunker can split a large table's rows across several chunks to
        stay within a token budget. Extracting spare parts, specifications,
        maintenance intervals, etc. from only a fragment of a table risks
        splitting a single row's fields across two separate LLM calls with
        no way to reassemble them. Hydrating restores the full table text on
        the first chunk that references it and drops the other chunks that
        reference the same table (their content is now redundant), so the
        extraction model always sees complete table rows.
        """
        seen_table_ids: set[str] = set()
        hydrated: list[DocumentChunk] = []
        for chunk in chunks:
            if not chunk.table_ids:
                hydrated.append(chunk)
                continue

            unseen_table_ids = [
                table_id for table_id in chunk.table_ids if table_id not in seen_table_ids
            ]
            if not unseen_table_ids:
                # Every table this chunk references was already hydrated in
                # full by an earlier chunk; this chunk is now redundant.
                continue
            seen_table_ids.update(unseen_table_ids)

            table_texts = [
                tables[table_id].to_embedding_text()
                for table_id in unseen_table_ids
                if table_id in tables and tables[table_id].has_content()
            ]
            if not table_texts:
                hydrated.append(chunk)
                continue

            hydrated.append(
                dataclass_replace(chunk, content="\n\n".join(table_texts))
            )
        return hydrated

    @staticmethod
    def _validate_input(
        document_id: str,
        chunks: list[DocumentChunk],
    ) -> None:
        validation = ValidationResult()

        if not document_id:
            validation.add_issue(
                "document_id",
                "Document id is required.",
                "extraction.document_id.required",
            )

        if not chunks:
            validation.add_issue(
                "chunks",
                "At least one chunk is required.",
                "extraction.chunks.required",
            )

        for index, chunk in enumerate(chunks):
            if chunk.document_id != document_id:
                validation.add_issue(
                    f"chunks[{index}].document_id",
                    "Chunk document_id must match the workflow document_id.",
                    "extraction.chunk.document_mismatch",
                )

        validation.raise_if_invalid()

    def _build_extraction_result(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
        response: str,
    ) -> ExtractionResult:
        self._invalid_source_chunk_id_events = []
        payload = self.response_parser.parse(response)
        chunk_lookup = {chunk.chunk_id: chunk for chunk in chunks}
        default_source_chunk_id = chunks[0].chunk_id if len(chunks) == 1 else None
        overall_confidence = payload["confidence_score"]
        maintenance_task_payloads = self._filter_empty_extraction_items(
            payload["maintenance_tasks"],
            content_keys=(
                "title",
                "task",
                "name",
                "description",
                "details",
                "interval",
                "frequency",
                "component_name",
                "component",
                "equipment_id",
            ),
        )
        spare_part_payloads = self._filter_empty_extraction_items(
            payload["spare_parts"],
            content_keys=(
                "part_number",
                "part",
                "description",
                "quantity",
                "qty",
                "component_name",
                "component",
                "manufacturer_name",
                "manufacturer",
            ),
        )
        equipment_payloads = self._filter_empty_extraction_items(
            payload["equipment"],
            content_keys=(
                "name",
                "equipment_name",
                "model_number",
                "model",
                "serial_number",
                "serial",
                "manufacturer_name",
                "manufacturer",
            ),
        )
        manufacturer_payloads = self._filter_empty_extraction_items(
            payload["manufacturers"],
            content_keys=(
                "name",
                "manufacturer_name",
                "website",
                "url",
                "country",
            ),
        )
        supplier_payloads = self._filter_empty_extraction_items(
            payload["suppliers"],
            content_keys=(
                "name",
                "supplier_name",
                "website",
                "url",
                "country",
            ),
        )
        procedure_payloads = self._filter_empty_extraction_items(
            payload["procedures"],
            content_keys=(
                "title",
                "steps",
                "component_name",
                "component",
            ),
        )
        specification_payloads = self._filter_empty_extraction_items(
            payload["specifications"],
            content_keys=(
                "parameter",
                "value",
                "unit",
                "component_name",
                "component",
            ),
        )
        safety_warning_payloads = self._filter_empty_extraction_items(
            payload["safety_warnings"],
            content_keys=(
                "warning_type",
                "message",
                "component_name",
                "component",
            ),
        )
        maintenance_interval_payloads = self._filter_empty_extraction_items(
            payload["maintenance_intervals"],
            content_keys=(
                "interval",
                "component_name",
                "component",
                "task_reference",
            ),
        )
        troubleshooting_entry_payloads = self._filter_empty_extraction_items(
            payload["troubleshooting_entries"],
            content_keys=(
                "symptom",
                "cause",
                "remedy",
                "component_name",
                "component",
            ),
        )
        identifier_payloads = self._filter_empty_extraction_items(
            payload["identifiers"],
            content_keys=(
                "raw_value",
                "value",
                "identifier_type",
                "type",
            ),
        )

        maintenance_tasks = [
            self._build_maintenance_task(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in maintenance_task_payloads
        ]
        spare_parts = [
            self._build_spare_part(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in spare_part_payloads
        ]
        equipment = [
            self._build_equipment_info(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in equipment_payloads
        ]
        manufacturers = [
            self._build_manufacturer(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in manufacturer_payloads
        ]
        suppliers = [
            self._build_supplier(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in supplier_payloads
        ]
        procedures = [
            self._build_procedure(
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
            self._build_specification(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in specification_payloads
        ]
        safety_warnings = [
            self._build_safety_warning(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in safety_warning_payloads
        ]
        maintenance_intervals = [
            self._build_maintenance_interval(
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
            self._build_troubleshooting_entry(
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
            self._build_extracted_identifier(
                item,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in identifier_payloads
        ]

        requires_human_review = self._resolve_requires_human_review(
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
                *procedures,
                *specifications,
                *safety_warnings,
                *maintenance_intervals,
                *troubleshooting_entries,
                *extracted_identifiers,
            ]
        )

        return ExtractionResult(
            extraction_id=self.id_generator.new_id(IdPrefix.EXTRACTION),
            document_id=document_id,
            maintenance_tasks=maintenance_tasks,
            spare_parts=spare_parts,
            equipment=equipment,
            manufacturers=manufacturers,
            suppliers=suppliers,
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

    def _build_maintenance_task(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> MaintenanceTask:
        title = self._required_text(
            payload,
            field_name="maintenance_tasks.title",
            keys=("title", "task", "name"),
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="maintenance_tasks",
        )

        return MaintenanceTask(
            task_id=self.id_generator.new_id("task"),
            document_id=document_id,
            title=title,
            description=self._optional_text(payload, "description", "details"),
            interval=self._optional_text(payload, "interval", "frequency"),
            component_name=self._optional_text(payload, "component_name", "component"),
            equipment_id=self._optional_text(payload, "equipment_id"),
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_spare_part(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> SparePart:
        part_number = self._optional_text(payload, "part_number", "part")
        description = self._optional_text(payload, "description")
        quantity = self._optional_text(payload, "quantity", "qty")
        component_name = self._optional_text(payload, "component_name", "component")
        manufacturer_name = self._optional_text(
            payload,
            "manufacturer_name",
            "manufacturer",
        )

        if not any(
            [
                part_number,
                description,
                quantity,
                component_name,
                manufacturer_name,
            ]
        ):
            raise SchemaValidationError(
                "spare_parts items must contain at least one supported field.",
                details={"spare_part": payload},
            )

        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="spare_parts",
        )

        return SparePart(
            spare_part_id=self.id_generator.new_id("spare"),
            document_id=document_id,
            part_number=part_number,
            description=description,
            quantity=quantity,
            component_name=component_name,
            manufacturer_name=manufacturer_name,
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_equipment_info(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> EquipmentInfo:
        name = self._optional_text(payload, "name", "equipment_name")
        model_number = self._optional_text(payload, "model_number", "model")
        serial_number = self._optional_text(payload, "serial_number", "serial")
        manufacturer_name = self._optional_text(
            payload,
            "manufacturer_name",
            "manufacturer",
        )

        if not any(
            [
                name,
                model_number,
                serial_number,
                manufacturer_name,
            ]
        ):
            raise SchemaValidationError(
                "equipment items must contain at least one supported field.",
                details={"equipment": payload},
            )

        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="equipment",
        )

        return EquipmentInfo(
            equipment_id=self.id_generator.new_id("equipment"),
            document_id=document_id,
            name=name,
            model_number=model_number,
            serial_number=serial_number,
            manufacturer_name=manufacturer_name,
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_manufacturer(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> Manufacturer:
        name = self._required_text(
            payload,
            field_name="manufacturers.name",
            keys=("name", "manufacturer_name"),
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="manufacturers",
        )

        return Manufacturer(
            manufacturer_id=self.id_generator.new_id("manufacturer"),
            document_id=document_id,
            name=name,
            website=self._optional_text(payload, "website", "url"),
            country=self._optional_text(payload, "country"),
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_supplier(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> Supplier:
        name = self._required_text(
            payload,
            field_name="suppliers.name",
            keys=("name", "supplier_name"),
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="suppliers",
        )

        return Supplier(
            supplier_id=self.id_generator.new_id("supplier"),
            document_id=document_id,
            name=name,
            website=self._optional_text(payload, "website", "url"),
            country=self._optional_text(payload, "country"),
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_procedure(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
        equipment: list[EquipmentInfo],
    ) -> Procedure:
        title = self._required_text(
            payload,
            field_name="procedures.title",
            keys=("title",),
        )
        raw_steps = self._pick(payload, "steps")
        steps = (
            [str(step).strip() for step in raw_steps if str(step).strip()]
            if isinstance(raw_steps, list)
            else []
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="procedures",
        )

        equipment_reference = self._optional_text(
            payload, "equipment_reference", "equipment_name", "equipment"
        )
        equipment_id = self._resolve_equipment_id(equipment_reference, equipment)

        try:
            procedure_type = ProcedureType(
                self._optional_text(payload, "procedure_type", "type")
                or ProcedureType.UNKNOWN.value
            )
        except ValueError:
            procedure_type = ProcedureType.UNKNOWN

        return Procedure(
            procedure_id=self.id_generator.new_id("procedure"),
            document_id=document_id,
            title=title,
            procedure_type=procedure_type,
            steps=steps,
            component_name=self._optional_text(payload, "component_name", "component"),
            equipment_id=equipment_id,
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_specification(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> Specification:
        parameter = self._required_text(
            payload,
            field_name="specifications.parameter",
            keys=("parameter",),
        )
        value = self._required_text(
            payload,
            field_name="specifications.value",
            keys=("value",),
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="specifications",
        )

        return Specification(
            specification_id=self.id_generator.new_id("specification"),
            document_id=document_id,
            parameter=parameter,
            value=value,
            unit=self._optional_text(payload, "unit"),
            component_name=self._optional_text(payload, "component_name", "component"),
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_safety_warning(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> SafetyWarning:
        message = self._required_text(
            payload,
            field_name="safety_warnings.message",
            keys=("message",),
        )
        warning_type = self._optional_text(payload, "warning_type") or "warning"
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="safety_warnings",
        )

        return SafetyWarning(
            safety_warning_id=self.id_generator.new_id("safety_warning"),
            document_id=document_id,
            warning_type=warning_type,
            message=message,
            component_name=self._optional_text(payload, "component_name", "component"),
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_maintenance_interval(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
        maintenance_tasks: list[MaintenanceTask],
    ) -> MaintenanceInterval:
        interval = self._required_text(
            payload,
            field_name="maintenance_intervals.interval",
            keys=("interval",),
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="maintenance_intervals",
        )

        task_reference = self._optional_text(payload, "task_reference")
        maintenance_task_id = self._resolve_maintenance_task_id(
            task_reference,
            maintenance_tasks,
        )

        return MaintenanceInterval(
            maintenance_interval_id=self.id_generator.new_id("maintenance_interval"),
            document_id=document_id,
            interval=interval,
            component_name=self._optional_text(payload, "component_name", "component"),
            maintenance_task_id=maintenance_task_id,
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    def _build_troubleshooting_entry(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
        equipment: list[EquipmentInfo],
    ) -> TroubleshootingEntry:
        symptom = self._required_text(
            payload,
            field_name="troubleshooting_entries.symptom",
            keys=("symptom",),
        )
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="troubleshooting_entries",
        )

        equipment_reference = self._optional_text(
            payload, "equipment_reference", "equipment_name", "equipment"
        )
        equipment_id = self._resolve_equipment_id(equipment_reference, equipment)

        return TroubleshootingEntry(
            troubleshooting_id=self.id_generator.new_id("troubleshooting"),
            document_id=document_id,
            symptom=symptom,
            cause=self._optional_text(payload, "cause"),
            remedy=self._optional_text(payload, "remedy"),
            component_name=self._optional_text(payload, "component_name", "component"),
            equipment_id=equipment_id,
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    @staticmethod
    def _resolve_maintenance_task_id(
        task_reference: str | None,
        maintenance_tasks: list[MaintenanceTask],
    ) -> str | None:
        if not task_reference:
            return None
        normalized_reference = task_reference.strip().lower()
        for task in maintenance_tasks:
            if task.title and task.title.strip().lower() == normalized_reference:
                return task.task_id
        for task in maintenance_tasks:
            normalized_title = (task.title or "").strip().lower()
            if normalized_title and (
                normalized_reference in normalized_title
                or normalized_title in normalized_reference
            ):
                return task.task_id
        return None

    @staticmethod
    def _resolve_equipment_id(
        equipment_reference: str | None,
        equipment: list[EquipmentInfo],
    ) -> str | None:
        if not equipment_reference:
            return None
        normalized_reference = equipment_reference.strip().lower()
        for item in equipment:
            candidates = (item.name, item.model_number)
            if any(
                candidate and candidate.strip().lower() == normalized_reference
                for candidate in candidates
            ):
                return item.equipment_id
        for item in equipment:
            candidates = (item.name, item.model_number)
            for candidate in candidates:
                normalized_candidate = (candidate or "").strip().lower()
                if normalized_candidate and (
                    normalized_reference in normalized_candidate
                    or normalized_candidate in normalized_reference
                ):
                    return item.equipment_id
        return None

    def _build_extracted_identifier(
        self,
        payload: dict[str, Any],
        *,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> ExtractedIdentifier:
        raw_value = self._required_text(
            payload,
            field_name="identifiers.raw_value",
            keys=("raw_value", "value"),
        )
        identifier_type = self._optional_text(payload, "identifier_type", "type") or "unknown"
        confidence_score = self._parse_confidence(
            self._pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = self._resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="identifiers",
        )

        return ExtractedIdentifier(
            raw_value=raw_value,
            identifier_type=identifier_type,
            source_chunk_id=source_chunk_id,
            confidence_score=confidence_score,
            requires_human_review=(
                self._resolve_requires_human_review(
                    self._pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )

    @staticmethod
    def _emit_progress(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)

    @staticmethod
    def _pick(payload: dict[str, Any], *keys: str) -> Any:
        normalized_payload = {
            KEY_PATTERN.sub("_", key.lower()).strip("_"): value
            for key, value in payload.items()
        }

        for key in keys:
            normalized_key = KEY_PATTERN.sub("_", key.lower()).strip("_")
            if normalized_key in normalized_payload:
                return normalized_payload[normalized_key]

        return None

    @classmethod
    def _required_text(
        cls,
        payload: dict[str, Any],
        *,
        field_name: str,
        keys: tuple[str, ...],
    ) -> str:
        value = cls._optional_text(payload, *keys)
        if value:
            return value

        raise SchemaValidationError(
            f"{field_name} is required.",
            details={field_name: payload},
        )

    @classmethod
    def _optional_text(cls, payload: dict[str, Any], *keys: str) -> str | None:
        value = cls._pick(payload, *keys)
        if value is None:
            return None

        text = " ".join(str(value).strip().strip('"').strip("'").split())
        text = text.rstrip(" .;:")
        if text.lower() in NULL_LIKE_TEXT_VALUES:
            return None
        return text or None

    @classmethod
    def _filter_empty_extraction_items(
        cls,
        items: list[dict[str, Any]],
        *,
        content_keys: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        return [
            item
            for item in items
            if cls._has_meaningful_item_content(item, content_keys=content_keys)
        ]

    @classmethod
    def _has_meaningful_item_content(
        cls,
        payload: dict[str, Any],
        *,
        content_keys: tuple[str, ...],
    ) -> bool:
        return any(cls._optional_text(payload, key) for key in content_keys)

    @staticmethod
    def _parse_confidence(value: Any) -> float | None:
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip().strip('"').strip("'").strip()
        if not text:
            return None

        try:
            if text.endswith("%"):
                return float(text[:-1].strip()) / 100

            return float(text)
        except ValueError:
            return None

    @staticmethod
    def _parse_bool(value: Any) -> bool | None:
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        text = str(value).strip().lower()
        if text in {"true", "yes", "1"}:
            return True

        if text in {"false", "no", "0"}:
            return False

        return None

    def _resolve_requires_human_review(
        self,
        raw_value: Any,
        confidence_score: float | None,
    ) -> bool:
        parsed_value = self._parse_bool(raw_value)
        if parsed_value is not None:
            return parsed_value

        if self.require_human_review_default:
            return True

        if confidence_score is None:
            return True

        return confidence_score < self.confidence_threshold

    def _resolve_source_chunk_id(
        self,
        payload: dict[str, Any],
        *,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        item_type: str,
    ) -> tuple[str | None, bool]:
        source_chunk_id = self._optional_text(
            payload,
            "source_chunk_id",
            "chunk_id",
        )
        if source_chunk_id is None:
            return default_source_chunk_id, False

        if source_chunk_id not in chunk_lookup:
            self._invalid_source_chunk_id_events.append(
                {
                    "item_type": item_type,
                    "invalid_source_chunk_id": source_chunk_id,
                    "fallback_source_chunk_id": default_source_chunk_id,
                    "available_chunk_ids": list(chunk_lookup),
                }
            )
            return default_source_chunk_id, True

        return source_chunk_id, False

    @staticmethod
    def _resolve_source_location(
        *,
        source_chunk_id: str | None,
        chunk_lookup: dict[str, DocumentChunk],
    ) -> SourceLocation:
        if source_chunk_id is None:
            return SourceLocation()

        chunk = chunk_lookup.get(source_chunk_id)
        if chunk is None:
            return SourceLocation()

        return SourceLocation(
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
            bbox=chunk.source.bbox,
        )
