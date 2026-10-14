from __future__ import annotations

from collections.abc import Callable

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
from src.application.workflows.extraction.candidates.extraction_prompt_narrowing_service import (
    ExtractionPromptNarrowingService,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.response import build_extraction_response_json_schema
from src.domain.extraction import ExtractionResult
from src.shared.activity import ActivityContext
from src.shared.exceptions import LLMProviderError, SchemaValidationError
from src.shared.progress.progress_emitter import emit_progress

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
        num_predict: int | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.extraction_model = extraction_model
        self.temperature = temperature
        self.json_mode = json_mode
        self.failure_preview_chars = failure_preview_chars
        self.prompt_narrowing_service = prompt_narrowing_service
        self.result_assembler = result_assembler
        self.num_predict = num_predict

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
            candidate_routing_diagnostics_sink=candidate_routing_diagnostics_sink,
        )
        prompt_sha256 = hash_prompt(prompt)
        prompt_sha256_canonical = hash_prompt_canonical(prompt)
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
        try:
            generation_result = self.llm_service.generate_with_metadata(
                prompt,
                model=self.extraction_model,
                activity_context=activity_context,
                temperature=self.temperature,
                json_mode=self.json_mode,
                response_schema=build_extraction_response_json_schema(),
                num_predict=self.num_predict,
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
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
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
                    f"[extraction {batch.batch_index}/{batch.batch_count}] "
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
                prompt_sha256=prompt_sha256,
                prompt_sha256_canonical=prompt_sha256_canonical,
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
                prompt_sha256=prompt_sha256,
                prompt_sha256_canonical=prompt_sha256_canonical,
                omitted_requested_family_keys=omitted_requested_family_keys(
                    requested_types, response
                ),
            )
        )
        return extraction_result
