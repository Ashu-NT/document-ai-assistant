from dataclasses import replace as dataclass_replace
from typing import Any
from collections.abc import Callable

from src.application.prompts.extraction import (
    CombinedExtractionPromptBuilder,
    ExtractionPromptType,
)
from src.application.prompts.extraction.narrowed import ExtractionNarrowedPromptBuilder
from src.application.services.ai import LLMService
from src.application.services.extraction import ExtractionService
from src.application.validation.common import ValidationResult
from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.common import (
    coerce_confidence_score,
    resolve_enum_value,
    resolve_setting,
    run_bounded_concurrent_map,
)
from src.application.workflows.extraction.batching import (
    ExtractionBatch,
    ExtractionBatchDiagnostics,
    ExtractionBatchOutcome,
    ExtractionChunkBatcher,
    safe_response_preview,
)
from src.application.workflows.extraction.candidates import (
    ExtractionCandidateLLMRouter,
    ExtractionCandidateSelector,
)
from src.application.workflows.extraction.context import (
    SemanticExtractionContext,
    SemanticExtractionContextBuilder,
)
from src.application.workflows.extraction.response import (
    ExtractionResponseParser,
    ExtractionResultMerger,
    build_extraction_response_json_schema,
)
from src.application.workflows.extraction.response.extraction_payload_field_picker import (
    optional_payload_text,
    pick_payload_value,
)
from src.domain.assets import TableAsset
from src.domain.common import SourceLocation
from src.domain.document import DocumentChunk, DocumentSection
from src.domain.extraction import (
    ContactPoint,
    ContactPointType,
    EquipmentInfo,
    ExtractedIdentifier,
    ExtractionResult,
    MaintenanceInterval,
    MaintenanceTask,
    Manufacturer,
    Procedure,
    ProcedureType,
    SafetyWarning,
    SemanticSourceMetadata,
    SemanticEntityType,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
)
from src.shared.activity import ActivityContext
from src.shared.collections import unique_in_order
from src.shared.execution import tracked_action
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator, IdPrefix
from src.shared.progress import emit_progress

_MAX_CONCURRENT_CANDIDATE_SELECTIONS = 8

# Per-entity "content" fields: the fields that actually carry extracted
# information, as opposed to bookkeeping (id/document_id/source_chunk_id/
# source/source_metadata/confidence_score/requires_human_review/audit,
# which every entity always has populated regardless of whether anything
# real was extracted) or a classification field that always defaults to a
# non-null placeholder (SafetyWarning.warning_type defaults to "warning",
# Procedure.procedure_type defaults to UNKNOWN — neither is evidence the
# LLM found real information, so neither counts as content here).
#
# Used as a final, entity-type-agnostic safety net right before saving: an
# extracted item can pass its per-field required-text checks during
# construction (e.g. by getting a non-empty single field) and still be
# effectively empty overall, or reach this point empty through some other
# path this per-field checking doesn't cover. Whatever the cause, an item
# with every content field null/empty apart from document_id/
# source_chunk_id must never be persisted.
_ENTITY_CONTENT_FIELDS: dict[type, tuple[str, ...]] = {
    MaintenanceTask: ("title", "description", "interval", "component_name", "equipment_id"),
    SparePart: ("part_number", "description", "quantity", "component_name", "manufacturer_name"),
    EquipmentInfo: ("name", "model_number", "serial_number", "manufacturer_name"),
    Manufacturer: ("name", "website", "country"),
    Supplier: ("name", "website", "country"),
    ContactPoint: ("value", "label", "owner_name"),
    Procedure: ("title", "steps", "component_name", "equipment_id"),
    Specification: ("parameter", "value", "unit", "component_name"),
    SafetyWarning: ("message", "component_name"),
    MaintenanceInterval: ("interval", "component_name", "maintenance_task_id"),
    TroubleshootingEntry: ("symptom", "cause", "remedy", "component_name", "equipment_id"),
}

def _default_extraction_model() -> str | None:
    def _load() -> str | None:
        from src.config.settings import llm_settings

        return llm_settings.extraction_llm or llm_settings.general_llm

    return resolve_setting(_load, None)


def _default_extraction_confidence_threshold() -> float:
    def _load() -> float:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_confidence_threshold

    return resolve_setting(_load, 1.0)


def _default_extraction_require_human_review() -> bool:
    def _load() -> bool:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_require_human_review

    return resolve_setting(_load, True)


def _default_max_chunks_per_batch() -> int:
    def _load() -> int:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_chunks_per_batch

    return resolve_setting(_load, 16)


def _default_max_chars_per_batch() -> int:
    def _load() -> int:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_chars_per_batch

    return resolve_setting(_load, 16_000)


def _default_allow_partial_batches() -> bool:
    def _load() -> bool:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_allow_partial_batches

    return resolve_setting(_load, False)


def _default_failure_preview_chars() -> int:
    def _load() -> int:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_failure_preview_chars

    return resolve_setting(_load, 1_200)


def _default_extraction_max_attempts() -> int:
    def _load() -> int:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_max_attempts

    return resolve_setting(_load, 2)


def _default_extraction_temperature() -> float:
    def _load() -> float:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_temperature

    return resolve_setting(_load, 0.0)


def _default_extraction_json_mode() -> bool:
    def _load() -> bool:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_json_mode

    return resolve_setting(_load, True)


def _default_candidate_narrowing_enabled() -> bool:
    def _load() -> bool:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_candidate_narrowing_enabled

    return resolve_setting(_load, False)


def _table_text_with_structured_rows(table: TableAsset) -> str:
    parts = [table.to_embedding_text()]
    structured_rows = table.to_structured_row_text()
    if structured_rows:
        parts.append(structured_rows)
    return "\n\n".join(parts)


def _normalize_enum_label_separators(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


_CONTACT_POINT_TYPE_ALIASES: dict[str, ContactPointType] = {
    "phone": ContactPointType.PHONE_NUMBER,
    "telephone": ContactPointType.PHONE_NUMBER,
    "telephone_number": ContactPointType.PHONE_NUMBER,
    "tel": ContactPointType.PHONE_NUMBER,
    "fax": ContactPointType.FAX_NUMBER,
    "fax_number": ContactPointType.FAX_NUMBER,
    "email": ContactPointType.EMAIL_ADDRESS,
    "email_address": ContactPointType.EMAIL_ADDRESS,
    "e_mail": ContactPointType.EMAIL_ADDRESS,
    "website": ContactPointType.URL,
    "web": ContactPointType.URL,
    "web_address": ContactPointType.URL,
}

_CONTACT_OWNER_ENTITY_TYPES = frozenset(
    {SemanticEntityType.MANUFACTURER, SemanticEntityType.SUPPLIER}
)


class ExtractionWorkflow:
    def __init__(
        self,
        llm_service: LLMService,
        extraction_service: ExtractionService,
        extraction_result_validator: ExtractionResultValidator,
        id_generator: IdGenerator,
        prompt_builder: CombinedExtractionPromptBuilder | None = None,
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
        semantic_context_builder: SemanticExtractionContextBuilder | None = None,
        candidate_selector: ExtractionCandidateSelector | None = None,
        narrowed_prompt_builder: ExtractionNarrowedPromptBuilder | None = None,
        enable_candidate_narrowing: bool | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.extraction_service = extraction_service
        self.extraction_result_validator = extraction_result_validator
        self.id_generator = id_generator
        self.prompt_builder = prompt_builder or CombinedExtractionPromptBuilder()
        self.response_parser = response_parser or ExtractionResponseParser()
        self.semantic_context_builder = (
            semantic_context_builder or SemanticExtractionContextBuilder()
        )
        self.candidate_selector = candidate_selector or ExtractionCandidateSelector(
            llm_router=ExtractionCandidateLLMRouter(llm_service=llm_service)
        )
        self.narrowed_prompt_builder = (
            narrowed_prompt_builder or ExtractionNarrowedPromptBuilder()
        )
        self.enable_candidate_narrowing = (
            enable_candidate_narrowing
            if enable_candidate_narrowing is not None
            else _default_candidate_narrowing_enabled()
        )
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
        self._semantic_contexts: dict[str, SemanticExtractionContext] = {}

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
        sections: dict[str, DocumentSection] | None = None,
        base_result: ExtractionResult | None = None,
    ) -> ExtractionResult:
        chunk_list = self._coerce_chunks(chunks)
        emit_progress(
            progress_callback,
            f"Preparing extraction input from {len(chunk_list)} final chunk(s)...",
        )
        self._validate_input(document_id, chunk_list)
        self.last_batch_diagnostics = []

        if tables:
            chunk_list = self._hydrate_table_chunks(chunk_list, tables)

        self._semantic_contexts = self.semantic_context_builder.build_all(
            document_id=document_id,
            chunks=chunk_list,
            sections=sections,
        )

        batches = self.chunk_batcher.build_batches(chunk_list)
        emit_progress(
            progress_callback,
            f"Prepared {len(batches)} extraction batch(es).",
        )
        partial_results: list[ExtractionResult] = (
            [dataclass_replace(base_result)] if base_result is not None else []
        )
        attempted_chunk_ids: list[str] = []
        unresolved_chunk_ids: list[str] = []
        for batch in batches:
            outcome = self._extract_batch_with_retries(
                document_id=document_id,
                batch=batch,
                activity_context=activity_context,
                progress_callback=progress_callback,
            )
            partial_results.extend(outcome.partial_results)
            attempted_chunk_ids.extend(outcome.attempted_chunk_ids)
            unresolved_chunk_ids.extend(outcome.unresolved_chunk_ids)

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

        carried_unresolved_chunk_ids = (
            [
                chunk_id
                for chunk_id in base_result.unresolved_chunk_ids
                if chunk_id not in {chunk.chunk_id for chunk in chunk_list}
            ]
            if base_result is not None
            else []
        )
        final_unresolved_chunk_ids = unique_in_order(
            [*carried_unresolved_chunk_ids, *unresolved_chunk_ids]
        )

        if final_unresolved_chunk_ids:
            emit_progress(
                progress_callback,
                (
                    "Extraction completed with unresolved chunk(s) pending retry: "
                    f"{final_unresolved_chunk_ids}."
                ),
            )

        extraction_result = self.result_merger.merge(
            document_id=document_id,
            partial_results=partial_results,
        )
        extraction_result.source_chunk_ids = unique_in_order(
            [
                *(
                    base_result.source_chunk_ids
                    if base_result is not None
                    else []
                ),
                *extraction_result.source_chunk_ids,
            ]
        )
        extraction_result.attempted_chunk_ids = unique_in_order(
            [
                *(
                    base_result.attempted_chunk_ids
                    if base_result is not None
                    else []
                ),
                *attempted_chunk_ids,
            ]
        )
        extraction_result.unresolved_chunk_ids = final_unresolved_chunk_ids
        extraction_result, dropped_empty_count = self._drop_empty_entities(
            extraction_result
        )
        if dropped_empty_count:
            emit_progress(
                progress_callback,
                (
                    f"Dropped {dropped_empty_count} extracted item(s) with no "
                    "real content (all fields null/empty apart from document/"
                    "chunk linkage) before saving."
                ),
            )
        extraction_result.requires_human_review = (
            self._resolve_requires_human_review(
                None,
                extraction_result.confidence_score,
            )
            or extraction_result.requires_human_review
            or bool(final_unresolved_chunk_ids)
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

        emit_progress(
            progress_callback,
            "Validating extraction result...",
        )
        validation = self.extraction_result_validator.validate(extraction_result)
        validation.raise_if_invalid()

        emit_progress(
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
        emit_progress(
            progress_callback,
            (
                "Extraction completed "
                f"(maintenance_tasks={len(extraction_result.maintenance_tasks)}, "
                f"spare_parts={len(extraction_result.spare_parts)}, "
                f"equipment={len(extraction_result.equipment)}, "
                f"manufacturers={len(extraction_result.manufacturers)}, "
                f"suppliers={len(extraction_result.suppliers)}, "
                f"contact_points={len(extraction_result.contact_points)}, "
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
    ) -> ExtractionBatchOutcome:
        last_exc: SchemaValidationError | None = None
        for attempt_index in range(1, self.max_attempts + 1):
            try:
                return ExtractionBatchOutcome(
                    partial_results=[
                        self._extract_batch_once(
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
                    ],
                    attempted_chunk_ids=list(batch.chunk_ids),
                )
            except SchemaValidationError as exc:
                last_exc = exc
                if attempt_index < self.max_attempts:
                    emit_progress(
                        progress_callback,
                        (
                            f"[extraction {batch.batch_index}/{batch.batch_count}] "
                            f"attempt {attempt_index}/{self.max_attempts} failed "
                            f"schema parsing: {exc}. Retrying this batch only..."
                        ),
                    )

        assert last_exc is not None
        if self.allow_partial_batches and len(batch.chunks) > 1:
            return self._isolate_persistently_failing_batch(
                document_id=document_id,
                batch=batch,
                activity_context=activity_context,
                progress_callback=progress_callback,
            )

        if self.allow_partial_batches:
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"failed after {self.max_attempts} attempt(s); marking chunk(s) "
                    f"{batch.chunk_ids} as unresolved and continuing with the "
                    "remaining batches."
                ),
            )
            return ExtractionBatchOutcome(
                attempted_chunk_ids=list(batch.chunk_ids),
                unresolved_chunk_ids=list(batch.chunk_ids),
            )

        raise last_exc

    def _isolate_persistently_failing_batch(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
    ) -> ExtractionBatchOutcome:
        single_chunk_batches = self.chunk_batcher.build_single_chunk_batches(batch)
        emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] "
                f"Persistently failing batch contains {len(batch.chunks)} chunk(s). "
                "Retrying each chunk individually to isolate only the failing ones..."
            ),
        )
        outcome = ExtractionBatchOutcome()
        for chunk_index, single_chunk_batch in enumerate(single_chunk_batches, start=1):
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"Isolating chunk {chunk_index}/{len(single_chunk_batches)}: "
                    f"{single_chunk_batch.chunk_ids[0]}"
                ),
            )
            outcome.extend(
                self._extract_batch_with_retries(
                    document_id=document_id,
                    batch=single_chunk_batch,
                    activity_context=activity_context,
                    progress_callback=progress_callback,
                )
            )
        return outcome

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
        emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] "
                f"Building extraction prompt from {len(batch.chunks)} chunk(s) "
                f"({batch.char_count} chars, {batch.word_count} words)..."
            ),
        )
        prompt, requested_types = self._build_prompt(
            document_id=document_id,
            batch=batch,
            previous_error=previous_error,
        )
        if requested_types is not None:
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    "Narrowed extraction to: "
                    f"{', '.join(sorted(t.value for t in requested_types))}"
                ),
            )
        emit_progress(
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
        emit_progress(
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
            emit_progress(
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
            emit_progress(
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

    def _build_prompt(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        previous_error: str | None,
    ) -> tuple[str, frozenset[ExtractionPromptType] | None]:
        """Builds the extraction prompt for a batch. Returns the prompt and,
        when narrowing actually reduced the requested types below the full
        set, the resolved type set (None otherwise) — used only to report
        what was narrowed via progress_callback.

        Falls back to the unnarrowed prompt_builder whenever narrowing is
        disabled or the batch's union of candidate types covers everything
        anyway, so the common case renders a byte-identical prompt to
        before this feature existed.
        """
        if not self.enable_candidate_narrowing or not batch.chunks:
            return (
                self.prompt_builder.build(
                    document_id, batch.chunks, previous_error=previous_error
                ),
                None,
            )

        # select_for_chunk() may call the (optional, off-by-default) LLM
        # candidate router per GENERAL/UNKNOWN chunk -- each call is an
        # independent, side-effect-free LLM request, so run them
        # concurrently instead of one at a time across the batch.
        selected_types = run_bounded_concurrent_map(
            batch.chunks,
            self.candidate_selector.select_for_chunk,
            max_concurrency=_MAX_CONCURRENT_CANDIDATE_SELECTIONS,
        )
        requested_types: frozenset[ExtractionPromptType] = frozenset().union(
            *selected_types
        )

        if requested_types == ExtractionCandidateSelector.all_types():
            return (
                self.prompt_builder.build(
                    document_id, batch.chunks, previous_error=previous_error
                ),
                None,
            )

        return (
            self.narrowed_prompt_builder.build(
                document_id,
                batch.chunks,
                requested_types=requested_types,
                previous_error=previous_error,
            ),
            requested_types,
        )

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
                _table_text_with_structured_rows(tables[table_id])
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
        # payload was already filtered by ExtractionResponseSanitizer.sanitize()
        # inside self.response_parser.parse() above -- no need to re-filter here.
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
        contact_points = [
            self._build_contact_point(
                item,
                document_id=document_id,
                chunk_lookup=chunk_lookup,
                default_source_chunk_id=default_source_chunk_id,
                default_confidence=overall_confidence,
            )
            for item in contact_point_payloads
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
            extraction_id=self.id_generator.new_id(IdPrefix.EXTRACTION),
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
            source_metadata=self._build_source_metadata(
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
            source_metadata=self._build_source_metadata(
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
            source_metadata=self._build_source_metadata(
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
            source_metadata=self._build_source_metadata(
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
            source_metadata=self._build_source_metadata(
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

    def _build_contact_point(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> ContactPoint:
        value = self._required_text(
            payload,
            field_name="contact_points.value",
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
            item_type="contact_points",
        )
        contact_type = self._resolve_contact_point_type(
            self._pick(payload, "contact_type", "type")
        )
        owner_entity_type = self._resolve_contact_owner_type(
            self._pick(payload, "owner_entity_type")
        )

        return ContactPoint(
            contact_point_id=self.id_generator.new_id("contact_point"),
            document_id=document_id,
            contact_type=contact_type,
            value=value,
            label=self._optional_text(payload, "label"),
            owner_name=self._optional_text(payload, "owner_name"),
            owner_entity_type=owner_entity_type,
            source_chunk_id=source_chunk_id,
            source=self._resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            source_metadata=self._build_source_metadata(
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

        procedure_type = resolve_enum_value(
            self._optional_text(payload, "procedure_type", "type"),
            ProcedureType,
            normalize=lambda text: text,
            default=ProcedureType.UNKNOWN,
        )

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
            source_metadata=self._build_source_metadata(
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
            source_metadata=self._build_source_metadata(
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
            source_metadata=self._build_source_metadata(
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
            source_metadata=self._build_source_metadata(
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
            source_metadata=self._build_source_metadata(
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
    def _resolve_contact_point_type(value: Any) -> ContactPointType:
        return resolve_enum_value(
            value,
            ContactPointType,
            normalize=_normalize_enum_label_separators,
            aliases=_CONTACT_POINT_TYPE_ALIASES,
            default=ContactPointType.UNKNOWN,
        )

    @staticmethod
    def _resolve_contact_owner_type(value: Any) -> SemanticEntityType | None:
        return resolve_enum_value(
            value,
            SemanticEntityType,
            normalize=_normalize_enum_label_separators,
            allowed_members=_CONTACT_OWNER_ENTITY_TYPES,
            default=None,
        )

    @staticmethod
    def _pick(payload: dict[str, Any], *keys: str) -> Any:
        return pick_payload_value(payload, *keys)

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
        return optional_payload_text(payload, *keys)

    def _drop_empty_entities(
        self, extraction_result: ExtractionResult
    ) -> tuple[ExtractionResult, int]:
        """Final safety net, run right before validation/save: drops any
        extracted entity whose content fields are all null/empty, no matter
        how it reached this point. See _ENTITY_CONTENT_FIELDS for what
        counts as content per entity type. Returns the result and how many
        items were dropped, for progress reporting."""
        field_lists = [
            ("maintenance_tasks", MaintenanceTask),
            ("spare_parts", SparePart),
            ("equipment", EquipmentInfo),
            ("manufacturers", Manufacturer),
            ("suppliers", Supplier),
            ("contact_points", ContactPoint),
            ("procedures", Procedure),
            ("specifications", Specification),
            ("safety_warnings", SafetyWarning),
            ("maintenance_intervals", MaintenanceInterval),
            ("troubleshooting_entries", TroubleshootingEntry),
        ]
        dropped_count = 0
        for attribute_name, entity_type in field_lists:
            original = getattr(extraction_result, attribute_name)
            kept = self._keep_non_empty(original, entity_type)
            dropped_count += len(original) - len(kept)
            setattr(extraction_result, attribute_name, kept)
        return extraction_result, dropped_count

    @classmethod
    def _keep_non_empty(cls, entities: list[Any], entity_type: type) -> list[Any]:
        content_fields = _ENTITY_CONTENT_FIELDS[entity_type]
        return [
            entity
            for entity in entities
            if cls._has_meaningful_entity_content(entity, content_fields)
        ]

    @staticmethod
    def _has_meaningful_entity_content(
        entity: Any,
        content_fields: tuple[str, ...],
    ) -> bool:
        for field_name in content_fields:
            value = getattr(entity, field_name, None)
            if isinstance(value, str):
                if value.strip():
                    return True
            elif isinstance(value, list):
                if value:
                    return True
            elif value is not None:
                return True
        return False

    @staticmethod
    def _parse_confidence(value: Any) -> float | None:
        return coerce_confidence_score(
            value,
            treat_bool_as_number=True,
            stringify_non_string_values=True,
        )

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

    def _build_source_metadata(
        self,
        *,
        source_chunk_id: str | None,
        chunk_lookup: dict[str, DocumentChunk],
    ) -> SemanticSourceMetadata | None:
        if source_chunk_id is None:
            return None

        if source_chunk_id not in chunk_lookup:
            return None

        context = self._semantic_contexts.get(source_chunk_id)
        if context is None:
            return None

        return context.to_source_metadata()
