from dataclasses import replace as dataclass_replace
from collections.abc import Callable

from src.application.prompts.extraction import CombinedExtractionPromptBuilder
from src.application.prompts.extraction.narrowed import ExtractionNarrowedPromptBuilder
from src.application.services.ai import LLMService
from src.application.services.extraction import ExtractionService
from src.application.validation.common import ValidationResult
from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.extraction.batching import (
    ExtractionBatchDiagnostics,
    ExtractionChunkBatcher,
)
from src.application.workflows.extraction.batching.extraction_batch_executor import (
    ExtractionBatchExecutor,
)
from src.application.workflows.extraction.batching.extraction_batch_retry_coordinator import (
    ExtractionBatchRetryCoordinator,
)
from src.application.workflows.extraction.batching.extraction_table_chunk_hydrator import (
    hydrate_table_chunks,
)
from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.candidates import (
    ExtractionCandidateLLMRouter,
    ExtractionCandidateSelector,
    ExtractionPromptNarrowingService,
)
from src.application.workflows.extraction.context import SemanticExtractionContextBuilder
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.extraction_workflow_settings import (
    _default_allow_partial_batches,
    _default_candidate_narrowing_enabled,
    _default_extraction_confidence_threshold,
    _default_extraction_json_mode,
    _default_extraction_max_attempts,
    _default_extraction_model,
    _default_extraction_require_human_review,
    _default_extraction_temperature,
    _default_failure_preview_chars,
    _default_max_chars_per_batch,
    _default_max_chunks_per_batch,
)
from src.application.workflows.extraction.pruning.empty_entity_pruner import (
    drop_empty_entities,
)
from src.application.workflows.extraction.response import (
    ExtractionResponseParser,
    ExtractionResultMerger,
)
from src.domain.assets import TableAsset
from src.domain.document import DocumentChunk, DocumentSection
from src.domain.extraction import ExtractionResult
from src.shared.activity import ActivityContext
from src.shared.collections.ordered_dedupe import unique_in_order
from src.shared.execution import tracked_action
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator
from src.shared.progress.progress_emitter import emit_progress


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

        self._builder_support = ExtractionBuilderSupport(
            confidence_threshold=self.confidence_threshold,
            require_human_review_default=self.require_human_review_default,
        )
        self._result_assembler = ExtractionResultAssembler(
            id_generator=id_generator,
            response_parser=self.response_parser,
            support=self._builder_support,
        )
        self._prompt_narrowing_service = ExtractionPromptNarrowingService(
            prompt_builder=self.prompt_builder,
            narrowed_prompt_builder=self.narrowed_prompt_builder,
            candidate_selector=self.candidate_selector,
            enable_candidate_narrowing=self.enable_candidate_narrowing,
        )
        self._batch_executor = ExtractionBatchExecutor(
            llm_service=self.llm_service,
            extraction_model=self.extraction_model,
            temperature=self.temperature,
            json_mode=self.json_mode,
            failure_preview_chars=self.failure_preview_chars,
            prompt_narrowing_service=self._prompt_narrowing_service,
            result_assembler=self._result_assembler,
        )
        self._batch_retry_coordinator = ExtractionBatchRetryCoordinator(
            max_attempts=self.max_attempts,
            allow_partial_batches=self.allow_partial_batches,
            chunk_batcher=self.chunk_batcher,
            batch_executor=self._batch_executor,
        )

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
            chunk_list = hydrate_table_chunks(chunk_list, tables)

        self._builder_support.set_semantic_contexts(
            self.semantic_context_builder.build_all(
                document_id=document_id,
                chunks=chunk_list,
                sections=sections,
            )
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
            outcome = self._batch_retry_coordinator.run(
                document_id=document_id,
                batch=batch,
                activity_context=activity_context,
                progress_callback=progress_callback,
                diagnostics_sink=self.last_batch_diagnostics,
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
        extraction_result, dropped_empty_count = drop_empty_entities(
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
            self._builder_support.resolve_requires_human_review(
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

    @staticmethod
    def _coerce_chunks(
        chunks: DocumentChunk | list[DocumentChunk],
    ) -> list[DocumentChunk]:
        if isinstance(chunks, list):
            return chunks

        return [chunks]

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

