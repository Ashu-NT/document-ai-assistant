from src.application.workflows.question_answering.question_answering_router import (
    QuestionAnsweringRouter,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.config.settings import retrieval_settings


class _FixedIntentInferer:
    def __init__(self, intent: RetrievalQueryIntent) -> None:
        self.intent = intent

    def resolve(self, query) -> RetrievalQueryIntent:
        return self.intent


class _PassthroughQueryAnalyzer:
    """Skips real intent classification so tests can pin a specific intent
    and deterministically exercise QuestionAnsweringRouter's top_k sizing
    logic, instead of depending on fuzzy natural-language classification."""

    def __init__(self, intent: RetrievalQueryIntent) -> None:
        self.intent_inferer = _FixedIntentInferer(intent)

    def analyze(self, query):
        return query


def test_decide_defaults_to_using_all_three_retrieval_sources() -> None:
    router = QuestionAnsweringRouter()

    _, analyzed, _ = router.decide("How do I change the oil?")

    assert analyzed.use_dense is True
    assert analyzed.use_keyword is True
    assert analyzed.use_sql is True


def test_decide_respects_a_disabled_retrieval_source(monkeypatch) -> None:
    # Regression guard: ENABLE_DENSE_RETRIEVAL/ENABLE_KEYWORD_RETRIEVAL/
    # ENABLE_SQL_RETRIEVAL were previously defined but never actually read --
    # RetrievalQuery.use_dense/use_keyword/use_sql were hardcoded True at
    # every construction site regardless of these settings.
    monkeypatch.setattr(retrieval_settings, "enable_sql_retrieval", False)
    router = QuestionAnsweringRouter()

    _, analyzed, _ = router.decide("How do I change the oil?")

    assert analyzed.use_sql is False
    assert analyzed.use_dense is True
    assert analyzed.use_keyword is True


def test_decide_sizes_top_k_up_for_a_troubleshooting_intent() -> None:
    router = QuestionAnsweringRouter(
        query_analyzer=_PassthroughQueryAnalyzer(RetrievalQueryIntent.TROUBLESHOOTING)
    )

    _, analyzed, intent = router.decide("Why is alarm E04 active?")

    assert intent == RetrievalQueryIntent.TROUBLESHOOTING
    assert analyzed.top_k > retrieval_settings.final_retrieval_top_k


def test_decide_sizes_top_k_down_for_an_identifier_intent() -> None:
    router = QuestionAnsweringRouter(
        query_analyzer=_PassthroughQueryAnalyzer(RetrievalQueryIntent.IDENTIFIER)
    )

    _, analyzed, intent = router.decide("What is part HP-001?")

    assert intent == RetrievalQueryIntent.IDENTIFIER
    assert analyzed.top_k < retrieval_settings.final_retrieval_top_k


def test_decide_explicit_top_k_wins_over_intent_sizing() -> None:
    router = QuestionAnsweringRouter(
        query_analyzer=_PassthroughQueryAnalyzer(RetrievalQueryIntent.TROUBLESHOOTING)
    )

    _, analyzed, _ = router.decide("Why is alarm E04 active?", top_k=1)

    assert analyzed.top_k == 1


def test_decide_uses_global_default_for_an_unlisted_intent() -> None:
    router = QuestionAnsweringRouter(
        query_analyzer=_PassthroughQueryAnalyzer(RetrievalQueryIntent.GENERAL)
    )

    _, analyzed, intent = router.decide("Tell me about this document.")

    assert intent == RetrievalQueryIntent.GENERAL
    assert analyzed.top_k == retrieval_settings.final_retrieval_top_k
