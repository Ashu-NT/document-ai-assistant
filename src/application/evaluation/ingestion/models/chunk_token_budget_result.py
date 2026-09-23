from dataclasses import dataclass, field
from enum import StrEnum


class ChunkTokenBudgetStatus(StrEnum):
    NORMAL = "normal"
    # token_count > effective_budget, AND the chunk is demonstrably already
    # at the minimum table-fragment granularity the production splitter can
    # ever produce (exactly one table row - see
    # ChunkTokenBudgetEvaluationResult's docstring for the exact proof).
    OVERSIZED_INDIVISIBLE = "oversized_indivisible"
    # token_count > effective_budget, and the chunk is NOT demonstrably at
    # that minimum granularity - a genuine regression candidate.
    HARD_BUDGET_VIOLATION = "hard_budget_violation"


@dataclass(slots=True, frozen=True)
class OversizedChunkDiagnostic:
    chunk_id: str
    token_count: int
    budget: int
    status: ChunkTokenBudgetStatus
    chunk_type: str
    table_id: str | None = None
    table_row_start: int | None = None
    table_row_end: int | None = None


@dataclass(slots=True, frozen=True)
class ChunkTokenBudgetEvaluationResult:
    """Per-document chunk-token-budget evaluation, using the EFFECTIVE
    chunking profile that actually produced this document's chunks (see
    `resolve_effective_chunking_profile`) rather than a maximum-across-all-
    profiles ceiling.

    A table-derived chunk is proven OVERSIZED_INDIVISIBLE (not merely
    assumed to be) when `table_row_start == table_row_end`: since
    `TableFragmentSplitter` only ever splits at row boundaries and never
    produces a fragment smaller than one row, a one-row fragment is *by
    construction* the finest granularity that splitter can ever produce -
    if it still exceeds budget, no further splitting was possible under the
    current production architecture. A chunk is never classified this way
    merely for having a `table_id`; a multi-row table fragment that still
    exceeds budget indicates production's own row-accumulation guard did
    not prevent an oversized group, which is a HARD_BUDGET_VIOLATION.

    The universal Phase 1 invariant is satisfied only when
    `hard_budget_violation_count == 0`. `oversized_indivisible_count` is a
    visible informational finding, never hidden and never counted as a
    failure.
    """

    resolved: bool
    profile: str | None = None
    effective_budget: int | None = None
    unresolved_reason: str | None = None
    max_observed_tokens: int | None = None
    normal_count: int = 0
    oversized_indivisible_count: int = 0
    hard_budget_violation_count: int = 0
    oversized_chunks: tuple[OversizedChunkDiagnostic, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        # Unresolved is an explicit non-pass, never a silent pass - the
        # invariant genuinely could not be checked, which must stay visible
        # rather than look identical to "checked and clean".
        return self.resolved and self.hard_budget_violation_count == 0


__all__ = [
    "ChunkTokenBudgetEvaluationResult",
    "ChunkTokenBudgetStatus",
    "OversizedChunkDiagnostic",
]
