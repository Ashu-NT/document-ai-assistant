from src.application.workflows.question_answering.answer_context.evidence_contradiction_detector import (
    EvidenceContradictionDetector,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
)


def _kv(key, value, unit=None, source_number=1, field_kind="specification"):
    return AnswerKeyValue(
        key=key, value=value, unit=unit, source_number=source_number, field_kind=field_kind
    )


def _maintenance_entry(task, interval, source_number):
    return AnswerMaintenanceEntry(
        task=task,
        interval=interval,
        component=None,
        notes=None,
        source_number=source_number,
        references=[AnswerMaintenanceReference(source_number=source_number)],
    )


def test_detects_a_genuine_specification_conflict_across_sources() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=2),
        ],
        maintenance_entries=[],
    )

    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.field_kind == "specification"
    assert set(conflict.values) == {"6 bar", "8 bar"}
    assert conflict.source_numbers == (1, 2)
    assert conflict.is_critical is True


def test_does_not_flag_unit_formatting_differences_as_a_conflict() -> None:
    """PR 10's explicit acceptance criterion: "1000 h" / "1,000 hours" /
    "1000 operating hours" must not look like disagreeing values."""
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Maximum operating hours", "1000 h", source_number=1),
            _kv("Maximum operating hours", "1,000 hours", source_number=2),
            _kv("Maximum operating hours", "1000 operating hours", source_number=3),
        ],
        maintenance_entries=[],
    )

    assert conflicts == []


def test_does_not_flag_pressure_unit_alias_differences_as_a_conflict() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Test pressure", "700", unit="bar", source_number=1),
            _kv("Test pressure", "700 bars", source_number=2),
        ],
        maintenance_entries=[],
    )

    assert conflicts == []


def test_detects_an_identifier_conflict_ignoring_punctuation_differences() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Part number", "PN-001", source_number=1, field_kind="identifier"),
            _kv("Part number", "PN 001", source_number=2, field_kind="identifier"),
        ],
        maintenance_entries=[],
    )

    # Same identifier once punctuation-normalized -- not a conflict.
    assert conflicts == []

    conflicts = detector.detect(
        key_values=[
            _kv("Part number", "PN-001", source_number=1, field_kind="identifier"),
            _kv("Part number", "PN-002", source_number=2, field_kind="identifier"),
        ],
        maintenance_entries=[],
    )

    assert len(conflicts) == 1
    assert conflicts[0].field_kind == "identifier"


def test_ignores_field_kinds_outside_the_narrow_scope() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Note", "A", source_number=1, field_kind="unknown"),
            _kv("Note", "B", source_number=2, field_kind="unknown"),
        ],
        maintenance_entries=[],
    )

    assert conflicts == []


def test_does_not_flag_a_single_source_multi_value_extraction_as_a_conflict() -> None:
    """Two distinct values for the same key, but both traced to the exact
    same source_number, is an extraction quirk from one messy chunk, not a
    genuine cross-source disagreement."""
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=1),
        ],
        maintenance_entries=[],
    )

    assert conflicts == []


def test_detects_a_maintenance_interval_conflict_across_sources() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[
            _maintenance_entry("Replace hydraulic filter", "500 hours", source_number=1),
            _maintenance_entry("Replace hydraulic filter", "1000 hours", source_number=2),
        ],
    )

    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.field_kind == "maintenance_interval"
    assert set(conflict.values) == {"500 hours", "1000 hours"}


def test_does_not_flag_not_specified_intervals_as_conflicting() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[
            _maintenance_entry("Replace hydraulic filter", "500 hours", source_number=1),
            _maintenance_entry("Replace hydraulic filter", "Not specified", source_number=2),
        ],
    )

    assert conflicts == []


def test_matches_maintenance_tasks_with_minor_wording_differences() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[
            _maintenance_entry("Replace the hydraulic filter", "500 hours", source_number=1),
            _maintenance_entry("Replace hydraulic filter", "1000 hours", source_number=2),
        ],
    )

    assert len(conflicts) == 1
