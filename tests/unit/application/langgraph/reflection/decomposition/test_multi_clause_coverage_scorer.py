from src.application.langgraph.reflection.decomposition import (
    MultiClauseCoverageScorer,
    QuestionClauses,
)


def test_all_clauses_covered_when_answer_shares_terms_with_each() -> None:
    scorer = MultiClauseCoverageScorer()
    clauses = QuestionClauses(
        clauses=(
            "What are the maintenance intervals",
            "what safety warnings apply?",
        )
    )

    result = scorer.score(
        clauses=clauses,
        answer_text=(
            "Weekly maintenance is required every 100 operating hours. "
            "Safety warnings include wearing protective equipment."
        ),
    )

    assert result.is_fully_covered is True
    assert result.uncovered_clauses == ()


def test_reports_the_uncovered_clause_when_the_answer_misses_it() -> None:
    scorer = MultiClauseCoverageScorer()
    clauses = QuestionClauses(
        clauses=(
            "What are the maintenance intervals",
            "what safety warnings apply?",
        )
    )

    result = scorer.score(
        clauses=clauses,
        answer_text="Weekly maintenance is required every 100 operating hours.",
    )

    assert result.is_fully_covered is False
    assert result.uncovered_clauses == ("what safety warnings apply?",)


def test_single_clause_is_covered_when_it_has_no_long_terms() -> None:
    scorer = MultiClauseCoverageScorer()
    clauses = QuestionClauses(clauses=("is it on",))

    result = scorer.score(clauses=clauses, answer_text="Yes.")

    assert result.is_fully_covered is True
