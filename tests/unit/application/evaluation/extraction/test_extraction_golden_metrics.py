from src.application.evaluation.extraction.extraction_applicability import (
    ExtractionApplicability,
)
from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_golden_metrics import (
    ApplicabilityCounts,
    ExtractionMetricsBucketKey,
    aggregate_extraction_metrics,
    summarize_buckets_by,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchOutcome,
    ExtractionMatchResult,
)

_KEY_PRESENCE = ExtractionMetricsBucketKey(
    document_alias="doc",
    entity_type="manufacturer",
    completeness=ExtractionCompleteness.PRESENCE_ONLY,
    review_status=ExtractionReviewStatus.CANDIDATE,
)
_KEY_EXHAUSTIVE = ExtractionMetricsBucketKey(
    document_alias="doc",
    entity_type="spare_part",
    completeness=ExtractionCompleteness.EXHAUSTIVE,
    review_status=ExtractionReviewStatus.REVIEWED,
)


def _match(outcome: ExtractionMatchOutcome, **overrides) -> ExtractionMatchResult:
    return ExtractionMatchResult(outcome=outcome, entity_type="x", **overrides)


class TestZeroDenominators:
    def test_recall_none_when_no_expectations(self) -> None:
        buckets = aggregate_extraction_metrics([])
        assert buckets == {}

    def test_precision_none_for_presence_only_even_with_data(self) -> None:
        buckets = aggregate_extraction_metrics(
            [(_KEY_PRESENCE, _match(ExtractionMatchOutcome.MATCHED))]
        )
        bucket = buckets[_KEY_PRESENCE]
        assert bucket.precision is None
        assert bucket.recall == 1.0
        assert bucket.f1 is None

    def test_precision_and_recall_none_when_bucket_has_no_tp_fp_fn(self) -> None:
        buckets = {
            _KEY_EXHAUSTIVE: aggregate_extraction_metrics(
                [(_KEY_EXHAUSTIVE, _match(ExtractionMatchOutcome.MATCHED))]
            )[_KEY_EXHAUSTIVE]
        }
        bucket = buckets[_KEY_EXHAUSTIVE]
        bucket.true_positive_count = 0
        assert bucket.precision is None
        assert bucket.recall is None
        assert bucket.f1 is None


class TestExhaustiveMetrics:
    def test_tp_fp_fn_precision_recall_f1(self) -> None:
        results = [
            (_KEY_EXHAUSTIVE, _match(ExtractionMatchOutcome.MATCHED)),
            (_KEY_EXHAUSTIVE, _match(ExtractionMatchOutcome.MATCHED)),
            (_KEY_EXHAUSTIVE, _match(ExtractionMatchOutcome.UNMATCHED_EXPECTED)),
            (_KEY_EXHAUSTIVE, _match(ExtractionMatchOutcome.UNMATCHED_ACTUAL)),
        ]
        buckets = aggregate_extraction_metrics(results)
        bucket = buckets[_KEY_EXHAUSTIVE]
        assert bucket.true_positive_count == 2
        assert bucket.false_negative_count == 1
        assert bucket.false_positive_count == 1
        assert bucket.precision == 2 / 3
        assert bucket.recall == 2 / 3
        assert round(bucket.f1, 4) == round(2 / 3, 4)

    def test_presence_only_unmatched_actual_never_becomes_a_false_positive(self) -> None:
        results = [
            (_KEY_PRESENCE, _match(ExtractionMatchOutcome.MATCHED)),
            (_KEY_PRESENCE, _match(ExtractionMatchOutcome.UNMATCHED_ACTUAL)),
        ]
        buckets = aggregate_extraction_metrics(results)
        bucket = buckets[_KEY_PRESENCE]
        assert bucket.false_positive_count == 0
        assert bucket.precision is None


class TestEvidenceCounters:
    def test_evidence_counts_only_recorded_for_matched(self) -> None:
        results = [
            (_KEY_PRESENCE, _match(ExtractionMatchOutcome.MATCHED, evidence_correct=True)),
            (_KEY_PRESENCE, _match(ExtractionMatchOutcome.MATCHED, evidence_correct=False)),
            (_KEY_PRESENCE, _match(ExtractionMatchOutcome.MATCHED, evidence_correct=None)),
        ]
        buckets = aggregate_extraction_metrics(results)
        bucket = buckets[_KEY_PRESENCE]
        assert bucket.evidence_correct_count == 1
        assert bucket.evidence_incorrect_count == 1
        assert bucket.evidence_not_checked_count == 1


class TestSummarizeBucketsBy:
    def test_filters_by_review_status(self) -> None:
        candidate_key = ExtractionMetricsBucketKey(
            document_alias="doc_a",
            entity_type="manufacturer",
            completeness=ExtractionCompleteness.PRESENCE_ONLY,
            review_status=ExtractionReviewStatus.CANDIDATE,
        )
        reviewed_key = ExtractionMetricsBucketKey(
            document_alias="doc_b",
            entity_type="manufacturer",
            completeness=ExtractionCompleteness.PRESENCE_ONLY,
            review_status=ExtractionReviewStatus.REVIEWED,
        )
        buckets = aggregate_extraction_metrics(
            [
                (candidate_key, _match(ExtractionMatchOutcome.MATCHED)),
                (reviewed_key, _match(ExtractionMatchOutcome.MATCHED)),
            ]
        )

        reviewed_only = summarize_buckets_by(buckets, only_review_status=ExtractionReviewStatus.REVIEWED)
        assert list(reviewed_only.keys()) == [("manufacturer", ExtractionCompleteness.PRESENCE_ONLY)]
        assert reviewed_only[("manufacturer", ExtractionCompleteness.PRESENCE_ONLY)].true_positive_count == 1

    def test_keeps_completeness_variants_separate_when_rolling_up(self) -> None:
        presence_key = ExtractionMetricsBucketKey(
            document_alias="doc_a",
            entity_type="safety_warning",
            completeness=ExtractionCompleteness.PRESENCE_ONLY,
            review_status=ExtractionReviewStatus.REVIEWED,
        )
        exhaustive_key = ExtractionMetricsBucketKey(
            document_alias="doc_b",
            entity_type="safety_warning",
            completeness=ExtractionCompleteness.EXHAUSTIVE,
            review_status=ExtractionReviewStatus.REVIEWED,
        )
        buckets = aggregate_extraction_metrics(
            [
                (presence_key, _match(ExtractionMatchOutcome.MATCHED)),
                (exhaustive_key, _match(ExtractionMatchOutcome.MATCHED)),
                (exhaustive_key, _match(ExtractionMatchOutcome.UNMATCHED_ACTUAL)),
            ]
        )

        rolled = summarize_buckets_by(buckets, only_review_status=ExtractionReviewStatus.REVIEWED)

        assert rolled[("safety_warning", ExtractionCompleteness.PRESENCE_ONLY)].precision is None
        assert rolled[("safety_warning", ExtractionCompleteness.EXHAUSTIVE)].precision == 0.5


class TestApplicabilityCounts:
    def test_records_each_state_independently(self) -> None:
        counts = ApplicabilityCounts()
        counts.record(ExtractionApplicability.APPLICABLE)
        counts.record(ExtractionApplicability.NOT_APPLICABLE)
        counts.record(ExtractionApplicability.NOT_APPLICABLE)
        counts.record(ExtractionApplicability.NOT_ASSESSED)

        assert counts.applicable == 1
        assert counts.not_applicable == 2
        assert counts.not_assessed == 1
