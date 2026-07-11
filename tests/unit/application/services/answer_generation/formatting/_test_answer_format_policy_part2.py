from src.application.services.answer_generation import AnswerFormatPolicy, AnswerIntent

from src.application.services.answer_generation.formatting.answer_format_policy import (
    _DIRECT_MAINTENANCE_RECORDS_INSTRUCTION,
    _ENTITY_GRAPH_AVAILABLE_INSTRUCTION,
    _EXACT_IDENTIFIER_ROWS_INSTRUCTION,
    _LOW_CONFIDENCE_EVIDENCE_INSTRUCTION,
    _MULTI_DOCUMENT_EVIDENCE_INSTRUCTION,
    _RAW_SOURCE_DOMINANT_INSTRUCTION,
    _RICH_STRUCTURED_EVIDENCE_INSTRUCTION,
    _SPARSE_EVIDENCE_INSTRUCTION,
    _TABLE_ROWS_AVAILABLE_INSTRUCTION,
)

from src.application.workflows.question_answering.answer_context import (
    AnswerKeyValue,
    AnswerRelationship,
    AnswerMaintenanceEntry,
    AnswerSource,
    AnswerStructuredEntity,
    StructuredAnswerContext,
)

def test_resolve_flags_raw_source_dominant_when_structure_is_absent() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.GENERAL,
        source_count=2,
        sources=[
            AnswerSource(source_number=1, chunk_id="chunk-1", content="Plain prose."),
            AnswerSource(source_number=2, chunk_id="chunk-2", content="More prose."),
        ],
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.GENERAL,
        structured_context=context,
    )

    assert policy.context_signals["raw_source_dominant"] is True
    assert _RAW_SOURCE_DOMINANT_INSTRUCTION in policy.instruction_lines

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
