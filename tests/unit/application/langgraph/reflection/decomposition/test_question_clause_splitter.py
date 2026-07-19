from src.application.langgraph.reflection.decomposition import QuestionClauseSplitter


def test_single_clause_question_is_unaffected() -> None:
    splitter = QuestionClauseSplitter()

    result = splitter.split("What is the pump operating pressure?")

    assert result.clauses == ("What is the pump operating pressure?",)
    assert result.has_multiple_clauses is False


def test_splits_a_conjunction_joined_multi_part_question() -> None:
    splitter = QuestionClauseSplitter()

    result = splitter.split(
        "What are the maintenance intervals, and what safety warnings apply?"
    )

    assert result.clauses == (
        "What are the maintenance intervals",
        "what safety warnings apply?",
    )
    assert result.has_multiple_clauses is True


def test_splits_two_question_mark_delimited_sentences() -> None:
    splitter = QuestionClauseSplitter()

    result = splitter.split(
        "What are the maintenance intervals? What safety warnings apply?"
    )

    assert result.clauses == (
        "What are the maintenance intervals?",
        "What safety warnings apply?",
    )
    assert result.has_multiple_clauses is True


def test_does_not_split_a_plain_noun_phrase_conjunction() -> None:
    """"and" joining two plain nouns (not two questions) must not be
    mistaken for a multi-clause question -- the second half doesn't start
    with a question trigger word and has no "?" of its own."""
    splitter = QuestionClauseSplitter()

    result = splitter.split(
        "What are the maintenance tasks and maintenance intervals?"
    )

    assert result.has_multiple_clauses is False


def test_handles_empty_and_none_input() -> None:
    splitter = QuestionClauseSplitter()

    assert splitter.split("").clauses == ("",)
    assert splitter.split(None).clauses == ("",)
    assert splitter.split("   ").clauses == ("",)
