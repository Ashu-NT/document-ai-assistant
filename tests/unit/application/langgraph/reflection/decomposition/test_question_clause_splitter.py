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


def test_splits_a_parenthesis_enumerated_request() -> None:
    splitter = QuestionClauseSplitter()

    result = splitter.split(
        "Tell me: 1) the spare parts list 2) the maintenance interval 3) any safety warnings"
    )

    assert result.clauses == (
        "Tell me: the spare parts list",
        "the maintenance interval",
        "any safety warnings",
    )
    assert result.has_multiple_clauses is True


def test_splits_a_period_enumerated_request() -> None:
    splitter = QuestionClauseSplitter()

    result = splitter.split("List 1. the part number 2. the serial number")

    assert result.clauses == ("List the part number", "the serial number")
    assert result.has_multiple_clauses is True


def test_does_not_split_on_a_single_enumerated_marker() -> None:
    """One marker isn't a list -- e.g. a stray "9." in prose must not be
    mistaken for the start of an enumeration."""
    splitter = QuestionClauseSplitter()

    result = splitter.split("The coefficient is 9. Then verify the reading.")

    assert result.has_multiple_clauses is False


def test_does_not_split_on_a_large_number_followed_by_a_period() -> None:
    """A number with more than one digit (e.g. an interval like "1000
    hours") must not be mistaken for a numbered-list marker."""
    splitter = QuestionClauseSplitter()

    result = splitter.split("Replace the filter at 1000. Then check oil level.")

    assert result.has_multiple_clauses is False


def test_does_not_split_on_out_of_order_markers() -> None:
    """Two numbers that happen to be followed by list-marker punctuation
    but aren't an ascending 1, 2, ... sequence are not a genuine
    enumeration."""
    splitter = QuestionClauseSplitter()

    result = splitter.split("Section 3. covers safety, section 2. covers maintenance.")

    assert result.has_multiple_clauses is False


def test_handles_empty_and_none_input() -> None:
    splitter = QuestionClauseSplitter()

    assert splitter.split("").clauses == ("",)
    assert splitter.split(None).clauses == ("",)
    assert splitter.split("   ").clauses == ("",)
