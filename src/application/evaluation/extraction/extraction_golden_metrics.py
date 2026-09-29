"""Metric model. Deliberately NOT one combined Phase 2B quality score - see
task instruction. Every bucket keeps reviewed/candidate and presence-only/
exhaustive separate, and every ratio is `None` (never a fabricated 0.0 or
1.0) whenever its denominator is zero or semantically undefined."""

from dataclasses import dataclass

from src.application.evaluation.extraction.extraction_applicability import (
    ExtractionApplicability,
)
from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchOutcome,
    ExtractionMatchResult,
)


@dataclass(frozen=True, slots=True)
class ExtractionMetricsBucketKey:
    document_alias: str
    entity_type: str
    completeness: ExtractionCompleteness
    review_status: ExtractionReviewStatus


@dataclass(slots=True)
class ExtractionMetricsBucket:
    key: ExtractionMetricsBucketKey
    true_positive_count: int = 0
    false_negative_count: int = 0
    false_positive_count: int = 0
    ambiguous_count: int = 0
    evidence_correct_count: int = 0
    evidence_incorrect_count: int = 0
    evidence_not_checked_count: int = 0

    @property
    def recall(self) -> float | None:
        denominator = self.true_positive_count + self.false_negative_count
        if denominator == 0:
            return None
        return self.true_positive_count / denominator

    @property
    def precision(self) -> float | None:
        if self.key.completeness is not ExtractionCompleteness.EXHAUSTIVE:
            return None
        denominator = self.true_positive_count + self.false_positive_count
        if denominator == 0:
            return None
        return self.true_positive_count / denominator

    @property
    def f1(self) -> float | None:
        precision = self.precision
        recall = self.recall
        if precision is None or recall is None:
            return None
        if precision + recall == 0:
            return None
        return 2 * precision * recall / (precision + recall)


def aggregate_extraction_metrics(
    match_results: list[tuple[ExtractionMetricsBucketKey, ExtractionMatchResult]],
) -> dict[ExtractionMetricsBucketKey, ExtractionMetricsBucket]:
    buckets: dict[ExtractionMetricsBucketKey, ExtractionMetricsBucket] = {}

    for key, match in match_results:
        bucket = buckets.setdefault(key, ExtractionMetricsBucket(key=key))

        if match.outcome is ExtractionMatchOutcome.MATCHED:
            bucket.true_positive_count += 1
            if match.evidence_correct is True:
                bucket.evidence_correct_count += 1
            elif match.evidence_correct is False:
                bucket.evidence_incorrect_count += 1
            else:
                bucket.evidence_not_checked_count += 1
        elif match.outcome is ExtractionMatchOutcome.UNMATCHED_EXPECTED:
            bucket.false_negative_count += 1
            if match.ambiguous_actual_entity_ids:
                bucket.ambiguous_count += 1
        elif match.outcome is ExtractionMatchOutcome.UNMATCHED_ACTUAL:
            if key.completeness is ExtractionCompleteness.EXHAUSTIVE:
                bucket.false_positive_count += 1

    return buckets


@dataclass(slots=True)
class ApplicabilityCounts:
    applicable: int = 0
    not_applicable: int = 0
    not_assessed: int = 0

    def record(self, applicability: ExtractionApplicability) -> None:
        if applicability is ExtractionApplicability.APPLICABLE:
            self.applicable += 1
        elif applicability is ExtractionApplicability.NOT_APPLICABLE:
            self.not_applicable += 1
        else:
            self.not_assessed += 1


def summarize_buckets_by(
    buckets: dict[ExtractionMetricsBucketKey, ExtractionMetricsBucket],
    *,
    only_review_status: ExtractionReviewStatus | None = None,
) -> dict[tuple[str, ExtractionCompleteness], ExtractionMetricsBucket]:
    """Rolls buckets up by (entity_type, completeness) across documents,
    optionally restricted to one review status - used to build the
    authoritative (REVIEWED-only) vs candidate (all) per-entity-type
    summary tables. Kept separate per completeness value rather than
    collapsed, since a PRESENCE_ONLY bucket's precision/F1 must stay
    undefined (None) even if another document annotated the same entity
    type EXHAUSTIVE."""
    rolled: dict[tuple[str, ExtractionCompleteness], ExtractionMetricsBucket] = {}
    for key, bucket in buckets.items():
        if only_review_status is not None and key.review_status is not only_review_status:
            continue
        rollup_key = (key.entity_type, key.completeness)
        rolled_key = ExtractionMetricsBucketKey(
            document_alias="__all__",
            entity_type=key.entity_type,
            completeness=key.completeness,
            review_status=key.review_status,
        )
        target = rolled.setdefault(
            rollup_key,
            ExtractionMetricsBucket(key=rolled_key),
        )
        target.true_positive_count += bucket.true_positive_count
        target.false_negative_count += bucket.false_negative_count
        target.false_positive_count += bucket.false_positive_count
        target.ambiguous_count += bucket.ambiguous_count
        target.evidence_correct_count += bucket.evidence_correct_count
        target.evidence_incorrect_count += bucket.evidence_incorrect_count
        target.evidence_not_checked_count += bucket.evidence_not_checked_count
    return rolled


def build_bucket_keyed_results(
    extraction_results: list,
) -> list[tuple[ExtractionMetricsBucketKey, ExtractionMatchResult]]:
    """Flattens `GoldenEvaluationReport.extraction_results` (per document ->
    per scope -> per match) into `(bucket_key, match)` pairs ready for
    `aggregate_extraction_metrics`. Each match already carries its own
    group completeness/review_status (see `ExtractionMatchResult`)."""
    keyed: list[tuple[ExtractionMetricsBucketKey, ExtractionMatchResult]] = []
    for document_result in extraction_results:
        for scope_outcome in document_result.scope_outcomes:
            for match in scope_outcome.match_results:
                key = ExtractionMetricsBucketKey(
                    document_alias=document_result.alias,
                    entity_type=match.entity_type,
                    completeness=match.group_completeness,
                    review_status=match.group_review_status,
                )
                keyed.append((key, match))
    return keyed


def collect_applicability_counts(
    extraction_results: list,
) -> ApplicabilityCounts:
    """Rolls up every `ExtractionApplicabilityDeclaration` actually attached
    to a scope outcome into one overall APPLICABLE/NOT_APPLICABLE/
    NOT_ASSESSED tally. A document/entity-type/scope combination with no
    declaration at all contributes nothing here - it is simply absent
    (NOT_ASSESSED is only counted when a declaration explicitly says so)."""
    counts = ApplicabilityCounts()
    for document_result in extraction_results:
        for scope_outcome in document_result.scope_outcomes:
            for declaration in scope_outcome.applicability_declarations:
                counts.record(declaration.applicability)
    return counts


__all__ = [
    "ExtractionMetricsBucketKey",
    "ExtractionMetricsBucket",
    "aggregate_extraction_metrics",
    "ApplicabilityCounts",
    "summarize_buckets_by",
    "build_bucket_keyed_results",
    "collect_applicability_counts",
]
