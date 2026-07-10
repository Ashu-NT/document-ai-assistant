from __future__ import annotations

from src.application.prompts.extraction import (
    CombinedExtractionPromptBuilder,
    ExtractionPromptType,
)
from src.application.prompts.extraction.narrowed import ExtractionNarrowedPromptBuilder
from src.application.workflows.common import run_bounded_concurrent_map
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
)

_MAX_CONCURRENT_CANDIDATE_SELECTIONS = 8


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
    ) -> tuple[str, frozenset[ExtractionPromptType] | None]:
        """Returns the prompt and, when narrowing actually reduced the
        requested types below the full set, the resolved type set (None
        otherwise) -- used only to report what was narrowed via
        progress_callback.

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
