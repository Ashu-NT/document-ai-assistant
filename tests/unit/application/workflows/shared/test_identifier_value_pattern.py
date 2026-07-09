from src.application.workflows.shared.identifier_value_pattern import (
    contains_identifier_value,
)


def test_detects_uppercase_alphanumeric_identifier() -> None:
    assert contains_identifier_value("Ordering code MK311007") is True


def test_detects_lowercase_alphanumeric_identifier_case_insensitively() -> None:
    assert contains_identifier_value("ordering code mk311007") is True


def test_detects_long_digit_sequence() -> None:
    assert contains_identifier_value("Order 123456-AB") is True


def test_returns_false_for_plain_prose_with_no_identifier_shape() -> None:
    assert contains_identifier_value("What is the operating pressure?") is False


def test_returns_false_for_hyphen_separated_prefix_and_number() -> None:
    """Known limitation of this pattern, not something this consolidation
    changes: a letters-hyphen-digits shape like 'HP-001' doesn't match
    ([A-Z]{1,5}\\d{1,6}... requires the digits immediately after the
    letters, no separator) since none of the three original call sites
    relied on that shape matching."""
    assert contains_identifier_value("Part number HP-001") is False


def test_returns_false_for_none() -> None:
    assert contains_identifier_value(None) is False


def test_returns_false_for_empty_string() -> None:
    assert contains_identifier_value("") is False
