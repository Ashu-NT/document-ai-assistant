from __future__ import annotations

from collections.abc import Callable

from src.application.services.ai import LLMService
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_batch_diagnostics import (
    ExtractionBatchDiagnostics,
    safe_response_preview,
)
from src.application.workflows.extraction.candidates.extraction_prompt_narrowing_service import (
    ExtractionPromptNarrowingService,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.response import build_extraction_response_json_schema
from src.domain.extraction import ExtractionResult
from src.shared.activity import ActivityContext
from src.shared.exceptions import SchemaValidationError
from src.shared.progress import emit_progress

# A single attempt at extracting one batch: build the (possibly narrowed)
# prompt, call the extraction model, and assemble the structured result --
# recording batch diagnostics either way. Split out of
# extraction_workflow.py's `_extract_batch_once`; retries across attempts
# are handled by the sibling `ExtractionBatchRetryCoordinator`.


class ExtractionBatchExecutor:
    def __init__(
        self,
        *,
        llm_service: LLMService,
        extraction_model: str | None,
        temperature: float,
        json_mode: bool,
        failure_preview_chars: int,
        prompt_narrowing_service: ExtractionPromptNarrowingService,
        result_assembler: ExtractionResultAssembler,
    ) -> None:
        self.llm_service = llm_service
        self.extraction_model = extraction_model
        self.temperature = temperature
        self.json_mode = json_mode
        self.failure_preview_chars = failure_preview_chars
        self.prompt_narrowing_service = prompt_narrowing_service
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
        emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] "
                f"Building extraction prompt from {len(batch.chunks)} chunk(s) "
                f"({batch.char_count} chars, {batch.word_count} words)..."
            ),
        )
        prompt, requested_types = self.prompt_narrowing_service.build_prompt(
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
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
                    f"Schema parsing failed: {exc}. "
                    f"Response preview: {compact_preview}"
                ),
            )
            raise SchemaValidationError(
                f"Extraction batch {batch.batch_index}/{batch.batch_count} failed schema parsing.",
                details=diagnostics.to_dict(),
            ) from exc

        if self.result_assembler.invalid_source_chunk_id_events:
            event_count = len(self.result_assembler.invalid_source_chunk_id_events)
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
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
