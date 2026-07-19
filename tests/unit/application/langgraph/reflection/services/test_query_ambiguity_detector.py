from src.application.langgraph.nodes.retrieval_intent_decision import (
    RetrievalIntentDecision,
)
from src.application.langgraph.reflection.services.query_ambiguity_detector import (
    QueryAmbiguityDetector,
)


class _ExplodingIntentInferer:
    def classify(self, query):
        raise AssertionError(
            "QueryAmbiguityDetector reclassified instead of using the "
            "supplied retrieval_intent_decision"
        )


def test_detect_uses_the_persisted_decision_without_reclassifying_on_a_tie() -> None:
    detector = QueryAmbiguityDetector(intent_inferer=_ExplodingIntentInferer())

    tie = detector.detect(
        "Show me the fault code table",
        retrieval_intent_decision=RetrievalIntentDecision(
            intent="table",
            best_score=4,
            runner_up_intent="troubleshooting",
            runner_up_score=4,
            gap=0,
            confidence=0.62,
        ),
    )

    assert tie is not None
    assert tie.intent_label == "table"
    assert tie.runner_up_label == "troubleshooting"


def test_detect_returns_none_for_a_persisted_decision_with_a_clear_winner() -> None:
    detector = QueryAmbiguityDetector(intent_inferer=_ExplodingIntentInferer())

    tie = detector.detect(
        "How do I start and run the macerator?",
        retrieval_intent_decision=RetrievalIntentDecision(
            intent="maintenance",
            best_score=6,
            runner_up_intent="table",
            runner_up_score=2,
            gap=4,
            confidence=0.82,
        ),
    )

    assert tie is None


def test_detect_returns_none_for_a_persisted_decision_with_no_runner_up() -> None:
    detector = QueryAmbiguityDetector(intent_inferer=_ExplodingIntentInferer())

    tie = detector.detect(
        "What is the maintenance interval?",
        retrieval_intent_decision=RetrievalIntentDecision(intent="maintenance"),
    )

    assert tie is None


def test_detect_falls_back_to_classifying_when_no_decision_is_supplied() -> None:
    # Compatibility fallback for callers that have no persisted decision to
    # read -- ReflectionService.review() (the one real caller) always
    # supplies one; this path is what keeps other/future callers working
    # until it's proven dead and removed.
    detector = QueryAmbiguityDetector()

    tie = detector.detect("Show me the fault code table")

    assert tie is not None
    assert tie.intent_label == "table"
    assert tie.runner_up_label == "troubleshooting"


def test_detect_returns_none_for_blank_question_with_no_decision() -> None:
    detector = QueryAmbiguityDetector(intent_inferer=_ExplodingIntentInferer())

    assert detector.detect(None) is None
    assert detector.detect("   ") is None
