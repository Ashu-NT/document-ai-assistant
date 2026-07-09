import logging

from src.application.services.answer_generation.intent import (
    AnswerIntent,
    AnswerIntentAnalyzer,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    ANSWER_INTENT_RULES_VERSION,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    *,
    content: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=chunk_type,
        section_path=["Section"],
        source=SourceLocation(page_start=1, page_end=1),
        metadata=metadata or {},
    )


def test_specification_question_maps_to_specification_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="specification",
        approved_chunks=[
            _make_chunk(
                content="Test pressure: 700 bar\nDesign pressure: 350 bar",
                chunk_type=ChunkType.CERTIFICATION_INFO,
            )
        ],
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY


def test_technical_data_question_maps_to_specification_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="technical data",
        approved_chunks=[_make_chunk(content="Voltage: 24 V")],
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY


def test_maintenance_interval_question_maps_to_maintenance_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="what are the maintenance interval?",
        approved_chunks=[
            _make_chunk(
                content="Maintenance interval: replace filter every 1000 hours.",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
            )
        ],
    )

    assert decision.intent == AnswerIntent.MAINTENANCE_SUMMARY


def test_maintenance_tasks_question_prefers_maintenance_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="What are maintenance tasks in the document?",
        chunk_type_preferences=[ChunkType.MAINTENANCE_PROCEDURE],
        approved_chunks=[
            _make_chunk(
                content="1. Check feed water pressure gauge\n2. Inspect the low pressure switch",
                chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
            )
        ],
    )

    assert decision.intent == AnswerIntent.MAINTENANCE_SUMMARY


def test_preventive_maintenance_question_maps_to_maintenance_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="Show preventive maintenance.",
        approved_chunks=[
            _make_chunk(
                content="Preventive maintenance: inspect the drive coupling every 6 months.",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
            )
        ],
    )

    assert decision.intent == AnswerIntent.MAINTENANCE_SUMMARY


def test_procedure_question_maps_to_procedure_steps() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="how do I replace the filter?",
        approved_chunks=[
            _make_chunk(
                content="1. Isolate the system\n2. Remove the cover\n3. Replace the filter",
                chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
            )
        ],
    )

    assert decision.intent == AnswerIntent.PROCEDURE_STEPS


def test_install_question_maps_to_procedure_steps() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="How do I install the pump?",
        approved_chunks=[
            _make_chunk(
                content="1. Position the pump\n2. Connect the inlet\n3. Connect the outlet",
                chunk_type=ChunkType.INSTALLATION_INSTRUCTION,
            )
        ],
    )

    assert decision.intent == AnswerIntent.PROCEDURE_STEPS


def test_warning_question_maps_to_safety_warnings() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="warning",
        approved_chunks=[
            _make_chunk(
                content="Warning: disconnect power before opening the enclosure.",
                chunk_type=ChunkType.SAFETY_WARNING,
            )
        ],
    )

    assert decision.intent == AnswerIntent.SAFETY_WARNINGS


def test_fault_cause_remedy_maps_to_troubleshooting() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="fault cause remedy",
        approved_chunks=[
            _make_chunk(
                content="Fault: pump will not start\nCause: fuse failed\nRemedy: replace fuse",
                chunk_type=ChunkType.TROUBLESHOOTING,
            )
        ],
    )

    assert decision.intent == AnswerIntent.TROUBLESHOOTING


def test_certificate_question_maps_to_certification_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="certificate inspection",
        approved_chunks=[
            _make_chunk(
                content="Certificate number: CER 1612\nInspection date: 29.11.2024",
                chunk_type=ChunkType.CERTIFICATION_INFO,
            )
        ],
    )

    assert decision.intent == AnswerIntent.CERTIFICATION_SUMMARY


def test_technical_specification_chunk_supports_specification_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="what is available?",
        chunk_type_preferences=[ChunkType.TECHNICAL_SPECIFICATION],
        approved_chunks=[_make_chunk(content="Voltage: 24 V")],
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY


def test_maintenance_interval_question_does_not_flip_to_specification_from_technical_values() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="What are the maintenance intervals?",
        chunk_type_preferences=[ChunkType.MAINTENANCE_INTERVAL],
        approved_chunks=[
            _make_chunk(
                content="Maintenance interval: inspect the pump weekly.",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
            ),
            _make_chunk(
                content="Voltage: 400 V. Installed power: 5.5 kW.",
                chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
            ),
        ],
    )

    assert decision.intent == AnswerIntent.MAINTENANCE_SUMMARY


def test_spare_parts_list_question_maps_to_table_summary_not_identifier_lookup() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="table of spare part list")

    assert decision.intent == AnswerIntent.TABLE_SUMMARY


def test_table_evidence_hydrated_metadata_triggers_table_like_signal_without_pipes() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="give me details",
        approved_chunks=[
            _make_chunk(
                content="Just some plain descriptive text with no pipe characters.",
                metadata={"table_evidence_hydrated": "true"},
            )
        ],
    )

    assert "context:table_like" in decision.matched_signals


def test_no_table_like_signal_without_pipes_or_hydration_metadata() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="give me details",
        approved_chunks=[
            _make_chunk(content="Just some plain descriptive text with no pipe characters.")
        ],
    )

    assert "context:table_like" not in decision.matched_signals


def test_spare_parts_list_question_with_evidence_maps_to_table_summary() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="table of spare part list",
        approved_chunks=[
            _make_chunk(
                content=(
                    "| Position No: | Qty: Denomination: Spare Part No: |\n"
                    "|---|---|\n"
                    "| 1 | 2 Filter 12345 |"
                ),
                chunk_type=ChunkType.SPARE_PARTS_TABLE,
            )
        ],
        chunk_type_preferences=[ChunkType.SPARE_PARTS_TABLE],
    )

    assert decision.intent == AnswerIntent.TABLE_SUMMARY


def test_list_all_part_numbers_still_maps_to_identifier_lookup() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="list all part numbers")

    assert decision.intent == AnswerIntent.IDENTIFIER_LOOKUP


def test_list_all_serial_numbers_still_maps_to_identifier_lookup() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="list all serial numbers")

    assert decision.intent == AnswerIntent.IDENTIFIER_LOOKUP


def test_explicit_question_overrides_weak_chunk_hint() -> None:
    decision = AnswerIntentAnalyzer().analyze(
        question="specification",
        chunk_type_preferences=[ChunkType.CERTIFICATION_INFO],
        approved_chunks=[
            _make_chunk(
                content="Test pressure: 700 bar\nDesign pressure: 350 bar",
                chunk_type=ChunkType.CERTIFICATION_INFO,
            )
        ],
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY


# ---------------------------------------------------------------------------
# Negation awareness: a term preceded by a negation cue within the lookback
# window no longer contributes to its intent's score (shares the exact
# cue/lookback logic RetrievalQueryIntentInferer uses, via the extracted
# negation_detection module).
# ---------------------------------------------------------------------------


def test_negated_terms_do_not_trigger_their_intent() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="This is not a safety warning.")

    assert decision.intent == AnswerIntent.GENERAL
    assert decision.matched_signals == []


def test_unnegated_terms_still_trigger_their_intent() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="This is a safety warning.")

    assert decision.intent == AnswerIntent.SAFETY_WARNINGS
    assert "question:safety" in decision.matched_signals


# ---------------------------------------------------------------------------
# Runner-up exposure: AnswerIntentDecision now surfaces the second-best
# intent/score instead of _confidence() computing and discarding it.
# ---------------------------------------------------------------------------


def test_exact_tie_exposes_the_runner_up_intent_and_score() -> None:
    """'specification'/'spec' (SPECIFICATION_SUMMARY, 2 hits x weight 6 = 12)
    and 'procedure'/'install' (PROCEDURE_STEPS, 2 hits x weight 6 = 12) tie
    exactly -- SPECIFICATION_SUMMARY wins via _INTENT_PRIORITY order, but the
    tie must now be visible on the decision rather than silently dropped."""
    decision = AnswerIntentAnalyzer().analyze(
        question="What is the specification and what is the procedure to install it?"
    )

    assert decision.intent == AnswerIntent.SPECIFICATION_SUMMARY
    assert decision.runner_up_intent == AnswerIntent.PROCEDURE_STEPS
    assert decision.runner_up_score == 12


def test_unambiguous_question_has_no_runner_up() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="This is a safety warning.")

    assert decision.runner_up_intent is None
    assert decision.runner_up_score == 0


# ---------------------------------------------------------------------------
# GENERAL fallback for genuinely ambiguous/empty input.
# ---------------------------------------------------------------------------


def test_empty_question_falls_back_to_general_with_no_runner_up() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="")

    assert decision.intent == AnswerIntent.GENERAL
    assert decision.confidence == 0.55
    assert decision.runner_up_intent is None
    assert decision.runner_up_score == 0


def test_question_with_no_recognizable_terms_falls_back_to_general() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="asdkjaslkdj")

    assert decision.intent == AnswerIntent.GENERAL
    assert decision.confidence == 0.55


# ---------------------------------------------------------------------------
# Structured logging, mirroring RetrievalQueryIntentInferer's log line shape.
# ---------------------------------------------------------------------------


def test_resolved_intent_is_logged_with_rules_version(caplog) -> None:
    with caplog.at_level(logging.INFO):
        AnswerIntentAnalyzer().analyze(question="This is a safety warning.")

    assert "answer_intent_resolved" in caplog.text
    assert "intent=safety_warnings" in caplog.text
    assert f"rules_version={ANSWER_INTENT_RULES_VERSION}" in caplog.text


def test_general_fallback_is_logged_with_reason(caplog) -> None:
    with caplog.at_level(logging.INFO):
        AnswerIntentAnalyzer().analyze(question="")

    assert "answer_intent_fallback_general" in caplog.text
    assert "reason=no_strong_signal" in caplog.text
