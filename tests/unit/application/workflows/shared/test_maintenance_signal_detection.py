from src.application.workflows.shared.maintenance_signal_detection import (
    mentions_maintenance_interval,
)


def test_detects_interval_phrase() -> None:
    assert mentions_maintenance_interval("what is the maintenance interval?")


def test_detects_bare_frequency_word() -> None:
    assert mentions_maintenance_interval("is this checked weekly?")


def test_detects_quarterly_marker_shared_by_both_consumers() -> None:
    assert mentions_maintenance_interval("is this a quarterly task?")


def test_detects_bare_schedule_marker_shared_by_both_consumers() -> None:
    assert mentions_maintenance_interval("what is the schedule for this?")


def test_returns_false_for_unrelated_text() -> None:
    assert not mentions_maintenance_interval("what is the operating pressure?")
