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
    hash_prompt,
    hash_prompt_canonical,
    safe_response_preview,
)
from src.application.workflows.extraction.batching.extraction_family_response_keys import (
    omitted_requested_family_keys,
)
from src.application.workflows.extraction.candidates.extraction_candidate_routing_diagnostics import (
    ExtractionCandidateRoutingDiagnostics,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.response import build_extraction_response_json_schema
from src.domain.extraction import ExtractionResult
from src.shared.activity import ActivityContext
from src.shared.exceptions import LLMProviderError, SchemaValidationError
from src.shared.progress.progress_emitter import emit_progress


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
        num_predict: int | None = None,
        num_ctx: int | None = None,
    ) -> None:
        self.entity_type = entity_type
        self.llm_service = llm_service
        self.extraction_model = extraction_model
        self.temperature = temperature
        self.json_mode = json_mode
        self.failure_preview_chars = failure_preview_chars
        self.result_assembler = result_assembler
        self.num_predict = num_predict
        self.num_ctx = num_ctx

    def execute_once(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        activity_context: ActivityContext | None,
        progress_callback: Callable[[str], None] | None,
        previous_error: str | None,
        diagnostics_sink: list[ExtractionBatchDiagnostics],
        candidate_routing_diagnostics_sink: (
            list[ExtractionCandidateRoutingDiagnostics] | None
        ) = None,
    ) -> ExtractionResult:
        # candidate_routing_diagnostics_sink is accepted-but-unused here:
        # SPECIALIZED_FAMILY's candidate routing decision already happened
        # once at plan-build time (build_extraction_plan), not per
        # attempt/executor call -- this parameter exists only so
        # ExtractionBatchRetryCoordinator can drive either executor
        # identically via duck typing (see this class's own module
        # docstring).
        del candidate_routing_diagnostics_sink
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
        prompt_sha256 = hash_prompt(prompt_result.prompt_text)
        prompt_sha256_canonical = hash_prompt_canonical(prompt_result.prompt_text)
        emit_progress(
            progress_callback,
            (
                f"[extraction {batch.batch_index}/{batch.batch_count}] [{label}] "
                f"Calling extraction model {self.extraction_model or 'default'}..."
            ),
        )
        try:
            generation_result = self.llm_service.generate_with_metadata(
                prompt_result.prompt_text,
                model=self.extraction_model,
                activity_context=activity_context,
                temperature=self.temperature,
                json_mode=self.json_mode,
                response_schema=build_extraction_response_json_schema(),
                num_predict=self.num_predict,
                num_ctx=self.num_ctx,
            )
        except LLMProviderError as exc:
            diagnostics = ExtractionBatchDiagnostics(
                batch_index=batch.batch_index,
                batch_count=batch.batch_count,
                chunk_ids=batch.chunk_ids,
                char_count=batch.char_count,
                word_count=batch.word_count,
                model_name=self.extraction_model,
                parse_success=False,
                parse_error=str(exc),
                prompt_sha256=prompt_sha256,
                prompt_sha256_canonical=prompt_sha256_canonical,
            )
            diagnostics_sink.append(diagnostics)
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] [{label}] "
                    f"LLM call failed ({exc.details.get('failure_kind', 'unknown')}): {exc}"
                ),
            )
            raise LLMProviderError(
                str(exc),
                details={**exc.details, **diagnostics.to_dict()},
            ) from exc

        response = generation_result.text
        if generation_result.finish_reason == "length":
            preview = safe_response_preview(response, max_chars=self.failure_preview_chars)
            diagnostics = ExtractionBatchDiagnostics(
                batch_index=batch.batch_index,
                batch_count=batch.batch_count,
                chunk_ids=batch.chunk_ids,
                char_count=batch.char_count,
                word_count=batch.word_count,
                model_name=self.extraction_model,
                parse_success=False,
                parse_error="Response truncated by output-length limit (finish_reason=length).",
                raw_response_preview=preview,
                prompt_sha256=prompt_sha256,
                prompt_sha256_canonical=prompt_sha256_canonical,
            )
            diagnostics_sink.append(diagnostics)
            emit_progress(
                progress_callback,
                (
                    f"[extraction {batch.batch_index}/{batch.batch_count}] [{label}] "
                    "Response truncated by output-length limit; treating as a failed attempt."
                ),
            )
            raise LLMProviderError(
                "Extraction response was truncated by the output-length limit.",
                details={"failure_kind": "truncated", **diagnostics.to_dict()},
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
                prompt_sha256=prompt_sha256,
                prompt_sha256_canonical=prompt_sha256_canonical,
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
                prompt_sha256=prompt_sha256,
                prompt_sha256_canonical=prompt_sha256_canonical,
                omitted_requested_family_keys=omitted_requested_family_keys(
                    frozenset({self.entity_type}), response
                ),
            )
        )
        return extraction_result
