from src.application.evaluation import (
    RetrievalBenchmarkCase,
    RetrievalBenchmarkCaseResult,
    RetrievalBenchmarkReport,
)
from src.application.workflows.retrieval.retrieval_query_intent import RetrievalQueryIntent
from src.domain.retrieval import RetrievalQuery


def _make_case(case_id: str, expected_intent: RetrievalQueryIntent | None) -> RetrievalBenchmarkCase:
    return RetrievalBenchmarkCase(
        case_id=case_id,
        query=RetrievalQuery(query_id=case_id, query_text="What is the safety warning?"),
        expected_intent=expected_intent,
    )


class TestIntentMatchProperty:
    def test_returns_none_when_case_has_no_expected_intent(self) -> None:
        result = RetrievalBenchmarkCaseResult(
            case=_make_case("c1", expected_intent=None),
            actual_intent=RetrievalQueryIntent.SAFETY,
        )
        assert result.intent_match is None

    def test_returns_true_when_actual_matches_expected(self) -> None:
        result = RetrievalBenchmarkCaseResult(
            case=_make_case("c1", expected_intent=RetrievalQueryIntent.SAFETY),
            actual_intent=RetrievalQueryIntent.SAFETY,
        )
        assert result.intent_match is True

    def test_returns_false_when_actual_differs_from_expected(self) -> None:
        result = RetrievalBenchmarkCaseResult(
            case=_make_case("c1", expected_intent=RetrievalQueryIntent.SAFETY),
            actual_intent=RetrievalQueryIntent.GENERAL,
        )
        assert result.intent_match is False

    def test_returns_false_when_actual_intent_was_never_set(self) -> None:
        result = RetrievalBenchmarkCaseResult(
            case=_make_case("c1", expected_intent=RetrievalQueryIntent.SAFETY),
        )
        assert result.intent_match is False


class TestIntentClassificationAccuracy:
    def test_ignores_cases_without_an_expected_intent(self) -> None:
        report = RetrievalBenchmarkReport(
            case_results=[
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c1", expected_intent=None),
                    actual_intent=RetrievalQueryIntent.SAFETY,
                ),
            ]
        )
        assert report.intent_classification_accuracy == 0.0

    def test_computes_accuracy_only_over_cases_with_an_expectation(self) -> None:
        report = RetrievalBenchmarkReport(
            case_results=[
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c1", expected_intent=RetrievalQueryIntent.SAFETY),
                    actual_intent=RetrievalQueryIntent.SAFETY,
                ),
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c2", expected_intent=RetrievalQueryIntent.PROCEDURE),
                    actual_intent=RetrievalQueryIntent.MAINTENANCE,
                ),
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c3", expected_intent=None),
                    actual_intent=RetrievalQueryIntent.GENERAL,
                ),
            ]
        )
        assert report.intent_classification_accuracy == 0.5

    def test_empty_report_has_zero_accuracy(self) -> None:
        assert RetrievalBenchmarkReport().intent_classification_accuracy == 0.0


class TestIntentConfusionMatrix:
    def test_builds_expected_vs_actual_counts_excluding_unset_expectations(self) -> None:
        report = RetrievalBenchmarkReport(
            case_results=[
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c1", expected_intent=RetrievalQueryIntent.SAFETY),
                    actual_intent=RetrievalQueryIntent.SAFETY,
                ),
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c2", expected_intent=RetrievalQueryIntent.SAFETY),
                    actual_intent=RetrievalQueryIntent.SAFETY,
                ),
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c3", expected_intent=RetrievalQueryIntent.PROCEDURE),
                    actual_intent=RetrievalQueryIntent.MAINTENANCE,
                ),
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c4", expected_intent=None),
                    actual_intent=RetrievalQueryIntent.GENERAL,
                ),
            ]
        )
        assert report.intent_confusion_matrix == {
            ("safety", "safety"): 2,
            ("procedure", "maintenance"): 1,
        }

    def test_missing_actual_intent_is_recorded_as_none(self) -> None:
        report = RetrievalBenchmarkReport(
            case_results=[
                RetrievalBenchmarkCaseResult(
                    case=_make_case("c1", expected_intent=RetrievalQueryIntent.SAFETY),
                ),
            ]
        )
        assert report.intent_confusion_matrix == {("safety", "none"): 1}
