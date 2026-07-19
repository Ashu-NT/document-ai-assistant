from src.application.workflows.question_answering.question_answering_router import (
    QuestionAnsweringRouter,
)
from src.config.settings import retrieval_settings


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
