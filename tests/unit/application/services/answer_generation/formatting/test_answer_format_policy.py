from src.application.services.answer_generation import AnswerFormatPolicy, AnswerIntent
from src.application.services.answer_generation.formatting.answer_format_policy import (
    _LOW_CONFIDENCE_EVIDENCE_INSTRUCTION,
    _MULTI_DOCUMENT_EVIDENCE_INSTRUCTION,
    _RICH_STRUCTURED_EVIDENCE_INSTRUCTION,
    _SPARSE_EVIDENCE_INSTRUCTION,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerSource,
    AnswerStructuredEntity,
    StructuredAnswerContext,
)


def test_specification_policy_uses_structured_bullets() -> None:
    policy = AnswerFormatPolicy.for_intent(AnswerIntent.SPECIFICATION_SUMMARY)

    assert policy.preferred_format == "structured_bullets"
    assert policy.include_bullets is True
    assert policy.include_table is True
    assert any(
        "Do not say that specifications are missing" in line
        for line in policy.instruction_lines
    )


def test_maintenance_policy_preserves_intervals() -> None:
    policy = AnswerFormatPolicy.for_intent(AnswerIntent.MAINTENANCE_SUMMARY)

    assert policy.preferred_format == "maintenance_numbered_entries"
    assert policy.include_table is False
    assert policy.include_bullets is False
    assert any("Not specified" in line for line in policy.instruction_lines)
    assert any("Do not output markdown tables" in line for line in policy.instruction_lines)


def test_maintenance_policy_resolve_is_stable_without_structured_entries() -> None:
    context = StructuredAnswerContext(answer_intent=AnswerIntent.MAINTENANCE_SUMMARY)

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.MAINTENANCE_SUMMARY,
        structured_context=context,
    )

    assert policy.preferred_format == "maintenance_numbered_entries"
    assert policy.include_table is False
    assert policy.include_bullets is False


def test_maintenance_policy_resolve_stays_numbered_with_structured_entries() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        maintenance_entries=[
            AnswerMaintenanceEntry(
                task="Replace cartridge filters",
                description="Replace cartridge filters every 1000 operating hours",
                interval="every 1000 operating hours",
                component="cartridge filters",
                notes=None,
                source_number=1,
            )
        ],
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.MAINTENANCE_SUMMARY,
        structured_context=context,
    )

    assert policy.preferred_format == "maintenance_numbered_entries"
    assert policy.include_table is False


def test_procedure_policy_uses_numbered_steps() -> None:
    policy = AnswerFormatPolicy.for_intent(AnswerIntent.PROCEDURE_STEPS)

    assert policy.include_steps is True
    assert policy.include_bullets is False
    assert policy.preferred_format == "numbered_steps"


def test_resolve_without_structured_context_returns_static_policy_unchanged() -> None:
    resolved = AnswerFormatPolicy.resolve(intent=AnswerIntent.GENERAL)
    static = AnswerFormatPolicy.for_intent(AnswerIntent.GENERAL)

    assert resolved == static
    assert resolved.context_signals == {}


def test_resolve_flags_sparse_evidence_when_at_most_one_source() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=1,
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["is_sparse_evidence"] is True
    assert _SPARSE_EVIDENCE_INSTRUCTION in policy.instruction_lines


def test_resolve_does_not_flag_sparse_evidence_with_multiple_sources() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=3,
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["is_sparse_evidence"] is False
    assert _SPARSE_EVIDENCE_INSTRUCTION not in policy.instruction_lines


def test_resolve_flags_low_confidence_evidence_below_threshold() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=2,
        key_values=[
            AnswerKeyValue(
                key="Serial Number",
                value="ABC-123",
                unit=None,
                source_number=1,
                confidence=0.4,
            )
        ],
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["has_low_confidence_evidence"] is True
    assert _LOW_CONFIDENCE_EVIDENCE_INSTRUCTION in policy.instruction_lines


def test_resolve_does_not_flag_low_confidence_evidence_at_deterministic_baseline() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=2,
        key_values=[
            AnswerKeyValue(
                key="Pressure",
                value="700 bar",
                unit="bar",
                source_number=1,
                confidence=0.9,
            )
        ],
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["has_low_confidence_evidence"] is False
    assert _LOW_CONFIDENCE_EVIDENCE_INSTRUCTION not in policy.instruction_lines


def test_resolve_flags_rich_structured_evidence_from_structured_entities() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=2,
        structured_entities=[
            AnswerStructuredEntity(entity_type="manufacturer", entity_id="manu-1")
        ],
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["has_rich_structured_evidence"] is True
    assert _RICH_STRUCTURED_EVIDENCE_INSTRUCTION in policy.instruction_lines


def test_resolve_flags_rich_structured_evidence_from_table_rows() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=2,
        sources=[
            AnswerSource(
                source_number=1,
                chunk_id="chunk-1",
                table_rows=[["Part", "Qty"], ["A-1", "2"]],
            )
        ],
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["has_rich_structured_evidence"] is True
    assert _RICH_STRUCTURED_EVIDENCE_INSTRUCTION in policy.instruction_lines


def test_resolve_flags_multi_document_evidence() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=2,
        diagnostics={"document_ids": ["doc-1", "doc-2"]},
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["is_multi_document"] is True
    assert _MULTI_DOCUMENT_EVIDENCE_INSTRUCTION in policy.instruction_lines


def test_resolve_does_not_flag_multi_document_evidence_for_single_document() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=2,
        diagnostics={"document_ids": ["doc-1"]},
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["is_multi_document"] is False
    assert _MULTI_DOCUMENT_EVIDENCE_INSTRUCTION not in policy.instruction_lines


def test_resolve_combines_multiple_signals_without_losing_base_instructions() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        source_count=1,
        diagnostics={"document_ids": ["doc-1", "doc-2"]},
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.SPECIFICATION_SUMMARY,
        structured_context=context,
    )

    base = AnswerFormatPolicy.for_intent(AnswerIntent.SPECIFICATION_SUMMARY)
    assert all(line in policy.instruction_lines for line in base.instruction_lines)
    assert _SPARSE_EVIDENCE_INSTRUCTION in policy.instruction_lines
    assert _MULTI_DOCUMENT_EVIDENCE_INSTRUCTION in policy.instruction_lines
    assert policy.preferred_format == base.preferred_format
    assert policy.include_table == base.include_table


def test_resolve_logs_context_adjustment_with_rules_version(caplog) -> None:
    import logging

    from src.application.services.answer_generation.formatting.answer_format_policy import (
        ANSWER_FORMAT_POLICY_RULES_VERSION,
    )

    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=1,
    )

    with caplog.at_level(logging.INFO):
        AnswerFormatPolicy.resolve(intent=AnswerIntent.GENERAL, structured_context=context)

    assert "answer_format_policy_context_adjusted" in caplog.text
    assert f"rules_version={ANSWER_FORMAT_POLICY_RULES_VERSION}" in caplog.text


def test_every_answer_intent_has_a_dedicated_format_policy_entry() -> None:
    """Exhaustiveness guard (plan section 9.8 / 4.15): AnswerFormatPolicy.for_intent()
    silently falls back to GENERAL's policy for any AnswerIntent missing from
    _POLICIES, via `_POLICIES.get(intent, _POLICIES[AnswerIntent.GENERAL])`. A
    new AnswerIntent member added later without a matching _POLICIES entry
    would pass every existing test (since GENERAL's policy is a valid
    AnswerFormatPolicy) while silently misformatting every answer for that
    intent. Checking `policy.intent == intent` distinguishes a real entry
    from a fallback -- a fallback carries GENERAL's own `intent` field, not
    the one that was requested."""
    for intent in AnswerIntent:
        policy = AnswerFormatPolicy.for_intent(intent)
        assert policy.intent == intent, (
            f"{intent} has no dedicated AnswerFormatPolicy entry and "
            "silently falls back to GENERAL's policy"
        )
