from dataclasses import dataclass
from enum import StrEnum

from src.application.evaluation.ingestion.models.chunk_token_budget_result import (
    ChunkTokenBudgetEvaluationResult,
)
from src.application.evaluation.ingestion.models.cross_reference_evaluation_result import (
    CrossReferenceEvaluationResult,
)
from src.application.evaluation.ingestion.models.ingestion_expectation_result import (
    IngestionExpectationCaseResult,
)


class GoldenDocumentEvaluationStatus(StrEnum):
    """Explicit per-document outcome of one fast-regression run. Every
    manifest entry gets exactly one of these - there is no silent "skipped,
    not mentioned" state (see GoldenEvaluationReport.documents_not_evaluated
    and the approved decision that a partial corpus must never be reported
    as a fully evaluated one)."""

    EVALUATED = "evaluated"
    CORPUS_MISSING = "corpus_missing"
    CORPUS_HASH_MISMATCH = "corpus_hash_mismatch"
    CACHE_MISS_IN_CACHED_ONLY_MODE = "cache_miss_in_cached_only_mode"
    PARSE_FAILED = "parse_failed"


@dataclass(slots=True)
class GoldenDocumentEvaluationOutcome:
    alias: str
    status: GoldenDocumentEvaluationStatus
    structural_result: IngestionExpectationCaseResult | None = None
    cross_reference_result: CrossReferenceEvaluationResult | None = None
    chunk_token_budget_result: ChunkTokenBudgetEvaluationResult | None = None
    detail: str | None = None

    @property
    def was_evaluated(self) -> bool:
        return self.status == GoldenDocumentEvaluationStatus.EVALUATED

    @property
    def structural_passed(self) -> bool:
        return self.structural_result is not None and self.structural_result.passed

    @property
    def has_structural_failures(self) -> bool:
        return self.structural_result is not None and not self.structural_result.passed


__all__ = ["GoldenDocumentEvaluationOutcome", "GoldenDocumentEvaluationStatus"]
