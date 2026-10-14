from __future__ import annotations

from src.application.prompts.extraction import (
    CombinedExtractionPromptBuilder,
    ExtractionPromptType,
)
from src.application.prompts.extraction.narrowed import ExtractionNarrowedPromptBuilder
from src.application.workflows.common.concurrent_chunk_runner import run_bounded_concurrent_map
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.candidates.extraction_candidate_routing_diagnostics import (
    ExtractionCandidateRoutingDiagnostics,
)
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
)

_MAX_CONCURRENT_CANDIDATE_SELECTIONS = 8


def resolve_requested_types(
    batch: ExtractionBatch,
    candidate_selector: ExtractionCandidateSelector,
    *,
    document_id: str | None = None,
    diagnostics_sink: list[ExtractionCandidateRoutingDiagnostics] | None = None,
) -> frozenset[ExtractionPromptType]:
    """Pure union-of-per-chunk-candidates computation: what entity families
    are worth requesting for this batch, per `candidate_selector`.

    Split out of `ExtractionPromptNarrowingService.build_prompt` (which still
    calls this and keeps its own enable/fallback behavior) so the
    SPECIALIZED_FAMILY execution strategy's plan-building
    (`extraction.specialized.extraction_plan.build_extraction_plan`) can reuse
    the EXACT SAME narrowing decision production's MULTI_FAMILY path already
    makes, instead of reimplementing or diverging from it. Returns
    `ExtractionCandidateSelector.all_types()` for an empty batch, matching
    `build_prompt`'s own empty-batch fallback.

    `document_id`/`diagnostics_sink` are purely observational (see
    `ExtractionCandidateRoutingDiagnostics`): omitting them (the default)
    reproduces this function's exact prior behavior and return value.
    """
    if not batch.chunks:
        return ExtractionCandidateSelector.all_types()

    # select_for_chunk() may call the LLM candidate router per GENERAL/
    # UNKNOWN chunk -- each call is an independent, side-effect-free LLM
    # request, so run them concurrently instead of one at a time across
    # the batch. executor.map() preserves input order in its results, so
    # `selected_types[i]` always corresponds to `batch.chunks[i]`.
    selected_types = run_bounded_concurrent_map(
        batch.chunks,
        lambda chunk: candidate_selector.select_for_chunk(
            chunk,
            diagnostics_sink=diagnostics_sink,
            document_id=document_id,
            batch_index=batch.batch_index,
            batch_count=batch.batch_count,
        ),
        max_concurrency=_MAX_CONCURRENT_CANDIDATE_SELECTIONS,
    )
    return frozenset().union(*selected_types)


class ExtractionPromptNarrowingService:
    """Builds the extraction prompt for a batch, optionally narrowing it to
    only the entity types a per-chunk candidate selector determined are
    plausibly present. Split out of extraction_workflow.py's `_build_prompt`.
    """

    def __init__(
        self,
        *,
        prompt_builder: CombinedExtractionPromptBuilder,
        narrowed_prompt_builder: ExtractionNarrowedPromptBuilder,
        candidate_selector: ExtractionCandidateSelector,
        enable_candidate_narrowing: bool,
    ) -> None:
        self.prompt_builder = prompt_builder
        self.narrowed_prompt_builder = narrowed_prompt_builder
        self.candidate_selector = candidate_selector
        self.enable_candidate_narrowing = enable_candidate_narrowing

    def build_prompt(
        self,
        *,
        document_id: str,
        batch: ExtractionBatch,
        previous_error: str | None,
        candidate_routing_diagnostics_sink: (
            list[ExtractionCandidateRoutingDiagnostics] | None
        ) = None,
    ) -> tuple[str, frozenset[ExtractionPromptType] | None]:
        """Returns the prompt and, when narrowing actually reduced the
        requested types below the full set, the resolved type set (None
        otherwise) -- used only to report what was narrowed via
        progress_callback.

        Falls back to the unnarrowed prompt_builder whenever narrowing is
        disabled or the batch's union of candidate types covers everything
        anyway, so the common case renders a byte-identical prompt to
        before this feature existed. `candidate_routing_diagnostics_sink`
        is purely observational and defaults to None, reproducing this
        method's exact prior behavior and return value.
        """
        if not self.enable_candidate_narrowing or not batch.chunks:
            return (
                self.prompt_builder.build(
                    document_id, batch.chunks, previous_error=previous_error
                ),
                None,
            )

        requested_types = resolve_requested_types(
            batch,
            self.candidate_selector,
            document_id=document_id,
            diagnostics_sink=candidate_routing_diagnostics_sink,
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
