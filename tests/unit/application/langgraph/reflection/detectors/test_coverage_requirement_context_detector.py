from src.application.langgraph.reflection.detectors.coverage_requirement_context_detector import (
    claims_completeness,
    has_step_sequence_gap,
)


def test_claims_completeness_detects_a_complete_list_phrase() -> None:
    assert claims_completeness("Here is the complete list of spare parts: ...") is True


def test_claims_completeness_returns_false_for_a_plain_answer() -> None:
    assert claims_completeness("Part number PN-001 is a hydraulic filter.") is False


def test_claims_completeness_handles_empty_text() -> None:
    assert claims_completeness("") is False
    assert claims_completeness(None) is False


def test_has_step_sequence_gap_detects_a_missing_step_marker() -> None:
    answer = "Step 1: Shut off power. Step 3: Remove the housing."
    assert has_step_sequence_gap(answer) is True


def test_has_step_sequence_gap_returns_false_for_a_contiguous_sequence() -> None:
    answer = "Step 1: Shut off power. Step 2: Drain fluid. Step 3: Remove the housing."
    assert has_step_sequence_gap(answer) is False


def test_has_step_sequence_gap_detects_a_gap_in_a_numbered_list() -> None:
    answer = "1. Shut off power.\n3. Remove the housing.\n"
    assert has_step_sequence_gap(answer) is True


def test_has_step_sequence_gap_returns_false_for_a_single_step() -> None:
    assert has_step_sequence_gap("Step 1: Shut off power.") is False


def test_has_step_sequence_gap_handles_empty_text() -> None:
    assert has_step_sequence_gap("") is False
    assert has_step_sequence_gap(None) is False
