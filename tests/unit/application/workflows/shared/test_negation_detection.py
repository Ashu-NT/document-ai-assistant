from src.application.workflows.shared.negation_detection import (
    has_non_negated_occurrence,
    is_negated,
)


def test_is_negated_true_when_cue_precedes_marker_within_lookback() -> None:
    text = "not a safety concern here"
    marker_start = text.index("safety")
    assert is_negated(text, marker_start) is True


def test_is_negated_false_when_no_cue_precedes_marker() -> None:
    text = "this is a safety concern"
    marker_start = text.index("safety")
    assert is_negated(text, marker_start) is False


def test_is_negated_false_when_cue_is_outside_lookback_window() -> None:
    text = "the pump was not running well but there is a safety issue"
    marker_start = text.index("safety")
    assert is_negated(text, marker_start) is False


def test_is_negated_true_for_multi_word_cue() -> None:
    text = "please describe topics unrelated to safety compliance"
    marker_start = text.index("safety")
    assert is_negated(text, marker_start) is True


def test_has_non_negated_occurrence_true_when_marker_absent_negation() -> None:
    assert has_non_negated_occurrence("this is a safety concern", "safety") is True


def test_has_non_negated_occurrence_false_when_only_occurrence_is_negated() -> None:
    assert has_non_negated_occurrence("not a safety concern", "safety") is False


def test_has_non_negated_occurrence_true_when_a_later_occurrence_is_not_negated() -> None:
    text = "this is not about danger, but the yellow tag indicates danger to operators"
    assert has_non_negated_occurrence(text, "danger") is True


def test_has_non_negated_occurrence_false_when_marker_never_appears() -> None:
    assert has_non_negated_occurrence("this is a safety concern", "hazard") is False


def test_is_negated_false_when_cue_is_only_a_substring_of_a_preceding_word() -> None:
    # Regression guard: "not" is a substring of "note" -- a plain
    # `cue in preceding_text` check incorrectly treated "please note the
    # safety warning" as negated.
    text = "please note the safety warning"
    marker_start = text.index("safety")
    assert is_negated(text, marker_start) is False


def test_has_non_negated_occurrence_true_when_cue_is_only_a_substring_of_a_preceding_word() -> None:
    assert (
        has_non_negated_occurrence("please note the safety warning", "safety")
        is True
    )
