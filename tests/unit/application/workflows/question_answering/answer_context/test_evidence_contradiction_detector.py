from src.application.workflows.question_answering.answer_context.evidence_contradiction_detector import (
    EvidenceContradictionDetector,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
    AnswerSource,
)
from src.domain.common import IdentifierType
from src.domain.document.entities.identifier import Identifier


def _source(
    source_number: int,
    document_id: str,
    *,
    chunk_type: str | None = None,
    section_path: str | None = None,
    content: str = "",
) -> AnswerSource:
    return AnswerSource(
        source_number=source_number,
        chunk_id=f"chunk_{source_number}",
        document_id=document_id,
        chunk_type=chunk_type,
        section_path=section_path,
        content=content,
    )


def _identifier(
    document_id: str,
    raw_value: str,
    identifier_type: IdentifierType = IdentifierType.MODEL_NUMBER,
) -> Identifier:
    return Identifier(
        identifier_id=f"id_{document_id}_{raw_value}",
        document_id=document_id,
        raw_value=raw_value,
        identifier_type=identifier_type,
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


def test_populates_document_ids_when_sources_are_provided() -> None:
    """PR 11 (answering_flow_weakness_remediation_plan.md): document_ids lets
    a consumer (ConflictingEvidenceGuardrail) tell a same-document conflict
    apart from one spanning multiple documents, without its own
    source_number -> document_id lookup."""
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=2),
        ],
        maintenance_entries=[],
        sources=[_source(1, "doc_a"), _source(2, "doc_b")],
    )

    assert len(conflicts) == 1
    assert conflicts[0].document_ids == ("doc_a", "doc_b")


def test_document_ids_collapses_to_one_when_sources_share_a_document() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=2),
        ],
        maintenance_entries=[],
        sources=[_source(1, "doc_a"), _source(2, "doc_a")],
    )

    assert len(conflicts) == 1
    assert conflicts[0].document_ids == ("doc_a",)


def test_document_ids_defaults_to_empty_when_sources_are_not_provided() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=2),
        ],
        maintenance_entries=[],
    )

    assert conflicts[0].document_ids == ()


# -- equipment-variant/document-revision normalization (W4 follow-up) -----


def test_suppresses_a_conflict_between_disjoint_equipment_variants() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=2),
        ],
        maintenance_entries=[],
        sources=[_source(1, "doc_a"), _source(2, "doc_b")],
        resolved_identifiers=[
            _identifier("doc_a", "HP-100"),
            _identifier("doc_b", "HP-200"),
        ],
    )

    assert conflicts == []


def test_still_flags_a_conflict_when_documents_share_a_model_number() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=2),
        ],
        maintenance_entries=[],
        sources=[_source(1, "doc_a"), _source(2, "doc_b")],
        resolved_identifiers=[
            _identifier("doc_a", "HP-100"),
            _identifier("doc_b", "HP-100"),
        ],
    )

    assert len(conflicts) == 1


def test_still_flags_a_conflict_when_model_numbers_are_not_resolved() -> None:
    """Backward compatibility: with no resolved_identifiers passed at all
    (every caller before this feature existed), behavior is unchanged."""
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=2),
        ],
        maintenance_entries=[],
        sources=[_source(1, "doc_a"), _source(2, "doc_b")],
    )

    assert len(conflicts) == 1


def test_ignores_non_model_number_identifiers_for_variant_suppression() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[
            _kv("Operating pressure", "6 bar", source_number=1),
            _kv("Operating pressure", "8 bar", source_number=2),
        ],
        maintenance_entries=[],
        sources=[_source(1, "doc_a"), _source(2, "doc_b")],
        resolved_identifiers=[
            _identifier("doc_a", "PN-100", identifier_type=IdentifierType.PART_NUMBER),
            _identifier("doc_b", "PN-200", identifier_type=IdentifierType.PART_NUMBER),
        ],
    )

    assert len(conflicts) == 1


# -- procedure-step order conflicts (W4 follow-up) -------------------------

_PROCEDURE_STEPS = """1. Turn off the pump.
2. Drain the tank.
3. Replace the filter."""

_PROCEDURE_STEPS_REORDERED = """1. Drain the tank.
2. Turn off the pump.
3. Replace the filter."""

_PROCEDURE_STEPS_SHORTER = """1. Turn off the pump.
2. Drain the tank."""


def test_detects_a_procedure_step_order_conflict_across_sources() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[],
        sources=[
            _source(
                1,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS,
            ),
            _source(
                2,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS_REORDERED,
            ),
        ],
    )

    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.field_kind == "procedure_step_order"
    assert conflict.source_numbers == (1, 2)


def test_does_not_flag_identical_step_order_as_a_conflict() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[],
        sources=[
            _source(
                1,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS,
            ),
            _source(
                2,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS,
            ),
        ],
    )

    assert conflicts == []


def test_does_not_flag_procedures_with_different_step_counts() -> None:
    """A shorter/longer step list is a completeness gap, not a genuine
    order disagreement."""
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[],
        sources=[
            _source(
                1,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS,
            ),
            _source(
                2,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS_SHORTER,
            ),
        ],
    )

    assert conflicts == []


def test_ignores_non_procedure_chunk_types_for_order_conflicts() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[],
        sources=[
            _source(
                1,
                "doc_a",
                chunk_type="specification_table",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS,
            ),
            _source(
                2,
                "doc_a",
                chunk_type="specification_table",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS_REORDERED,
            ),
        ],
    )

    assert conflicts == []


def test_ignores_different_sections_for_order_conflicts() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[],
        sources=[
            _source(
                1,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS,
            ),
            _source(
                2,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Oil Change",
                content=_PROCEDURE_STEPS_REORDERED,
            ),
        ],
    )

    assert conflicts == []


def test_suppresses_a_procedure_order_conflict_between_different_equipment_variants() -> None:
    detector = EvidenceContradictionDetector()

    conflicts = detector.detect(
        key_values=[],
        maintenance_entries=[],
        sources=[
            _source(
                1,
                "doc_a",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS,
            ),
            _source(
                2,
                "doc_b",
                chunk_type="maintenance_procedure",
                section_path="Filter Replacement",
                content=_PROCEDURE_STEPS_REORDERED,
            ),
        ],
        resolved_identifiers=[
            _identifier("doc_a", "HP-100"),
            _identifier("doc_b", "HP-200"),
        ],
    )

    assert conflicts == []
