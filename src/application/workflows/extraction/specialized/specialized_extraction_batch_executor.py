from __future__ import annotations

from collections.abc import Callable

from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.services.ai import LLMService
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_batch_diagnostics import (
    ExtractionBatchDiagnostics,
    safe_response_preview,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.response import build_extraction_response_json_schema
from src.domain.extraction import ExtractionResult
from src.shared.activity import ActivityContext
from src.shared.exceptions import SchemaValidationError
from src.shared.progress.progress_emitter import emit_progress

# SPECIALIZED_FAMILY twin of ExtractionBatchExecutor: bound to exactly one
# entity family at construction time. Builds its prompt via
# ExtractionPromptFactory (one of the existing, modular per-family builders
# in EXTRACTION_PROMPT_REGISTRY) instead of ExtractionPromptNarrowingService,
# then reuses the EXACT SAME response_schema/parsing/assembly path as
# MULTI_FAMILY -- ExtractionResponsePayload's per-family defaults already
# accept a response containing only this family's key, so no parser/builder
# change was needed for a single-family response to work. Structurally
# mirrors ExtractionBatchExecutor.execute_once's control flow (including its
# SchemaValidationError/diagnostics behavior) so ExtractionBatchRetryCoordinator
# can drive either executor identically via duck typing.


class SpecializedExtractionBatchExecutor:
    def __init__(
        self,
        *,
        entity_type: ExtractionPromptType,
        llm_service: LLMService,
        extraction_model: str | None,
        temperature: float,
        json_mode: bool,
        failure_preview_chars: int,
        result_assembler: ExtractionResultAssembler,
    ) -> None:
        self.entity_type = entity_type
        self.llm_service = llm_service
        self.extraction_model = extraction_model
        self.temperature = temperature
        self.json_mode = json_mode
        self.failure_preview_chars = failure_preview_chars
        self.result_assembler = result_assembler

    def execute_once(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        previous_error: str | None,
        diagnostics_sink: list[ExtractionBatchDiagnostics],
    ) -> ExtractionResult:
        label = f"specialized:{self.entity_type.value}"
        emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] [{label}] "
                f"Building extraction prompt from {len(batch.chunks)} chunk(s) "
                f"({batch.char_count} chars, {batch.word_count} words)..."
            ),
        )
        prompt_result = ExtractionPromptFactory.build(
            self.entity_type,
            ExtractionPromptContext(
                document_id=document_id,
                chunks=batch.chunks,
                previous_error=previous_error,
            ),
        )
        emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] [{label}] "
                f"Calling extraction model {self.extraction_model or 'default'}..."
            ),
        )
        response = self.llm_service.generate(
            prompt_result.prompt_text,
            model=self.extraction_model,
            activity_context=activity_context,
            temperature=self.temperature,
            json_mode=self.json_mode,
            response_schema=build_extraction_response_json_schema(),
        )
        emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] [{label}] "
                "Extraction model response received. Parsing structured payload..."
            ),
        )
        try:
            extraction_result = self.result_assembler.build(
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
            diagnostics_sink.append(diagnostics)
            compact_preview = " ".join(preview.split())
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] [{label}] "
                    f"Schema parsing failed: {exc}. "
                    f"Response preview: {compact_preview}"
                ),
            )
            raise SchemaValidationError(
                f"Specialized extraction batch {batch.batch_index}/{batch.batch_count} "
                f"(family={self.entity_type.value}) failed schema parsing.",
                details=diagnostics.to_dict(),
            ) from exc

        if self.result_assembler.invalid_source_chunk_id_events:
            event_count = len(self.result_assembler.invalid_source_chunk_id_events)
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] [{label}] "
                    f"{event_count} item(s) referenced a source_chunk_id outside "
                    "this batch; flagged for human review and pinned to a "
                    "fallback chunk instead of failing the batch."
                ),
            )

        diagnostics_sink.append(
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
