from __future__ import annotations

from dataclasses import dataclass, field

from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.candidates.extraction_candidate_routing_diagnostics import (
    ExtractionCandidateRoutingDiagnostics,
)
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
)
from src.application.workflows.extraction.candidates.extraction_prompt_narrowing_service import (
    resolve_requested_types,
)

# The SPECIALIZED_FAMILY execution strategy's deterministic work breakdown:
# one ExtractionWorkItem per (batch, candidate entity family) pair, built
# from the SAME batches ExtractionChunkBatcher already produces and the SAME
# per-chunk candidate signal (ExtractionCandidateSelector) MULTI_FAMILY
# narrowing already uses -- see resolve_requested_types. Nothing here
# consults golden/expected extraction data: the planner only ever sees
# batches (chunks + their ChunkType/content) and the selector's own
# deterministic rules.


@dataclass(slots=True, frozen=True)
class ExtractionWorkItem:
    """One unit of specialized-family extraction work: extract exactly
    `entity_type` from exactly `batch`'s evidence chunks."""

    entity_type: ExtractionPromptType
    batch: ExtractionBatch


@dataclass(slots=True, frozen=True)
class ExtractionPlan:
    work_items: list[ExtractionWorkItem] = field(default_factory=list)


def build_extraction_plan(
    batches: list[ExtractionBatch],
    *,
    candidate_selector: ExtractionCandidateSelector,
    document_id: str | None = None,
    candidate_routing_diagnostics_sink: (
        list[ExtractionCandidateRoutingDiagnostics] | None
    ) = None,
) -> ExtractionPlan:
    """Expands each batch into one ExtractionWorkItem per candidate-narrowed
    entity family. Deterministic: for the same batches and selector, always
    produces the same work items in the same order (families sorted by
    their string value within each batch).

    `document_id`/`candidate_routing_diagnostics_sink` are purely
    observational and default to None, reproducing this function's exact
    prior behavior and return value.
    """
    work_items: list[ExtractionWorkItem] = []
    for batch in batches:
        requested_types = resolve_requested_types(
            batch,
            candidate_selector,
            document_id=document_id,
            diagnostics_sink=candidate_routing_diagnostics_sink,
        )
        for entity_type in sorted(requested_types, key=lambda t: t.value):
            work_items.append(
                ExtractionWorkItem(entity_type=entity_type, batch=batch)
            )

    return ExtractionPlan(work_items=work_items)
