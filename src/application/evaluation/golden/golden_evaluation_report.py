from collections import Counter
from dataclasses import dataclass, field

from src.application.evaluation.classification.classification_golden_metrics import (
    ClassificationGoldenMetrics,
    compute_classification_golden_metrics,
)
from src.application.evaluation.classification.golden_classification_document_result import (
    GoldenClassificationDocumentResult,
)
from src.application.evaluation.golden.aggregate_cross_reference_metrics import (
    AggregateCrossReferenceTypeMetrics,
    aggregate_cross_reference_type_metrics,
)
from src.application.evaluation.golden.corpus_coverage_summary import (
    CorpusCoverageSummary,
)
from src.application.evaluation.extraction.golden_extraction_document_result import (
    GoldenExtractionDocumentResult,
)
from src.application.evaluation.golden.golden_document_evaluation_outcome import (
    GoldenDocumentEvaluationOutcome,
)
from src.application.evaluation.ingestion.ingestion_expectation_evaluator import (
    UNIVERSAL_INVARIANT_ASSERTION_NAMES,
)
from src.application.evaluation.reproducibility import EvaluationRunMetadata


@dataclass(slots=True)
class GoldenEvaluationReport:
    run_metadata: EvaluationRunMetadata
    corpus_coverage: CorpusCoverageSummary
    document_outcomes: list[GoldenDocumentEvaluationOutcome] = field(default_factory=list)
    # Sibling to document_outcomes (parsing/structural stage) rather than an
    # extension of it - the classification stage has its own outcome model
    # (see ClassificationStageStatus) and its own, separate golden-label
    # source. Empty by default so every Phase 1 caller/report is unaffected.
    classification_results: list[GoldenClassificationDocumentResult] = field(
        default_factory=list
    )
    # Same convention, for the Phase 2B extraction stage (see
    # ExtractionStageStatus) - empty by default so every Phase 1/2A
    # caller/report is unaffected.
    extraction_results: list[GoldenExtractionDocumentResult] = field(
        default_factory=list
    )

    @property
    def classification_metrics(self) -> ClassificationGoldenMetrics:
        return compute_classification_golden_metrics(self.classification_results)

    @property
    def structural_passed_count(self) -> int:
        return sum(1 for outcome in self.document_outcomes if outcome.structural_passed)

    @property
    def structural_failed_count(self) -> int:
        return sum(
            1 for outcome in self.document_outcomes if outcome.has_structural_failures
        )

    @property
    def documents_not_evaluated(self) -> list[GoldenDocumentEvaluationOutcome]:
        return [
            outcome for outcome in self.document_outcomes if not outcome.was_evaluated
        ]

    @property
    def chunk_invariant_failure_count(self) -> int:
        count = 0
        for outcome in self.document_outcomes:
            if outcome.structural_result is None:
                continue
            count += sum(
                1
                for assertion in outcome.structural_result.failed_assertions
                if assertion.name in UNIVERSAL_INVARIANT_ASSERTION_NAMES
            )
        return count

    @property
    def structural_assertion_failure_count(self) -> int:
        count = 0
        for outcome in self.document_outcomes:
            if outcome.structural_result is None:
                continue
            count += sum(
                1
                for assertion in outcome.structural_result.failed_assertions
                if assertion.name not in UNIVERSAL_INVARIANT_ASSERTION_NAMES
            )
        return count

    @property
    def chunk_token_budget_hard_violation_count(self) -> int:
        return sum(
            outcome.chunk_token_budget_result.hard_budget_violation_count
            for outcome in self.document_outcomes
            if outcome.chunk_token_budget_result is not None
        )

    @property
    def chunk_token_budget_oversized_indivisible_count(self) -> int:
        return sum(
            outcome.chunk_token_budget_result.oversized_indivisible_count
            for outcome in self.document_outcomes
            if outcome.chunk_token_budget_result is not None
        )

    @property
    def chunk_token_budget_unresolved_aliases(self) -> tuple[str, ...]:
        return tuple(
            outcome.alias
            for outcome in self.document_outcomes
            if outcome.chunk_token_budget_result is not None
            and not outcome.chunk_token_budget_result.resolved
        )

    @property
    def cross_reference_type_metrics(self) -> list[AggregateCrossReferenceTypeMetrics]:
        all_type_metrics = [
            metrics
            for outcome in self.document_outcomes
            if outcome.cross_reference_result is not None
            for metrics in outcome.cross_reference_result.type_metrics
        ]
        return aggregate_cross_reference_type_metrics(all_type_metrics)

    @property
    def reconciliation_outcome_counts(self) -> dict[str, int]:
        totals: Counter[str] = Counter()
        for outcome in self.document_outcomes:
            if outcome.cross_reference_result is None:
                continue
            totals.update(outcome.cross_reference_result.reconciliation_outcome_counts)
        return dict(totals)


__all__ = ["GoldenEvaluationReport"]
