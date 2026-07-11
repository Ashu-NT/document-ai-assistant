from src.application.langgraph.reflection.detectors.identifier_inventory_context_detector import (
    answer_contains_identifier_inventory,
)

_UNRELATED_LABEL_AND_VALUE_FAR_APART = (
    "No part number system is documented; the unit is rated DN50."
)

_IDENTIFIER_VALUE_NEAR_ITS_LABEL = (
    "The part number is A00103, printed on the equipment nameplate."
)


def test_label_and_identifier_value_in_unrelated_clauses_is_not_satisfied() -> None:
    """Reproduces the exact investigation misfire (finding 4.4b): the label
    'part number' and the identifier-shaped 'DN50' coincidentally both
    appear in the answer, but in unrelated clauses separated by a semicolon
    -- this must no longer be treated as satisfying an identifier-inventory
    request."""
    assert answer_contains_identifier_inventory(_UNRELATED_LABEL_AND_VALUE_FAR_APART) is False


def test_identifier_value_appearing_right_after_its_label_is_satisfied() -> None:
    assert answer_contains_identifier_inventory(_IDENTIFIER_VALUE_NEAR_ITS_LABEL) is True


def test_explicit_requested_identifiers_phrase_still_satisfies() -> None:
    assert answer_contains_identifier_inventory(
        "Here are the requested identifiers for this equipment."
    ) is True


def test_labeled_list_header_still_satisfies() -> None:
    assert answer_contains_identifier_inventory(
        "Serial Numbers: SN12345, SN67890"
    ) is True


def test_no_identifier_marker_at_all_is_not_satisfied() -> None:
    assert answer_contains_identifier_inventory(
        "This document describes pumps, valves, and safety procedures."
    ) is False
