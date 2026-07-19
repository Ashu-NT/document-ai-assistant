import pytest

from src.application.services.answer_generation import AnswerIntent
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.application.workflows.question_answering.answer_context import (
    StructuredAnswerContext,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
    AnswerIntentDecision,
)
from src.domain.common import ChunkType, IdentifierType
from src.domain.common.source_location import SourceLocation
from src.domain.document.entities.identifier import Identifier
from src.domain.retrieval.retrieved_chunk import RetrievedChunk
from src.shared.exceptions import SchemaValidationError

from tests.unit.application.services.answer_generation._answer_generation_service_support import (
    FakeLLMService,
    _make_chunk,
    _make_citation,
    make_service,
)


def test_generate_builds_citations_from_chunks_with_citation() -> None:
    citation = _make_citation("chunk_001")
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(
            question="Test?",
            context_chunks=[
                _make_chunk(chunk_id="chunk_001", citation=citation),
                _make_chunk(chunk_id="chunk_002", citation=None),
            ],
        )
    )
    assert len(result.citations) == 1
    assert result.citations[0] is citation
    assert result.cited_chunk_ids == ["chunk_001"]


def test_generate_empty_citations_when_no_chunk_has_citation() -> None:
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(
            question="Any question?",
            context_chunks=[_make_chunk(chunk_id=f"c{i}", citation=None) for i in range(3)],
        )
    )
    assert result.citations == []
    assert result.cited_chunk_ids == []


def test_generate_uses_deterministic_identifier_renderer_and_skips_llm() -> None:
    llm = FakeLLMService(response="This answer should not be used.")
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="list all serial and part nmubers",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            resolved_identifiers=[
                Identifier("id_part", "doc_001", raw_value="PN-001", identifier_type=IdentifierType.PART_NUMBER),
                Identifier("id_serial", "doc_001", raw_value="SN-9001", identifier_type=IdentifierType.SERIAL_NUMBER),
            ],
        )
    )
    assert "Requested identifiers" in result.answer_text
    assert "Part Numbers:" in result.answer_text
    assert "- PN-001" in result.answer_text
    assert "Serial Numbers:" in result.answer_text
    assert "- SN-9001" in result.answer_text
    assert result.model_name == "deterministic_identifier_renderer"
    assert llm.calls == []


def test_generate_bypasses_the_identifier_renderer_for_conflicting_evidence() -> None:
    """PR 10 (answering_flow_weakness_remediation_plan.md, W4): a critical
    cross-source contradiction must route to the LLM path instead of
    letting the deterministic renderer format disagreeing values with no
    way to flag the disagreement -- same request as the renderer-fires
    test above, except the structured_context now carries a conflict."""
    llm = FakeLLMService(
        response='{"answer_text":"Sources disagree on the part number; flagging for review."}'
    )
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="list all serial and part nmubers",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            resolved_identifiers=[
                Identifier("id_part", "doc_001", raw_value="PN-001", identifier_type=IdentifierType.PART_NUMBER),
            ],
            structured_context=StructuredAnswerContext(
                answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
                diagnostics={"has_critical_evidence_conflict": True},
            ),
        )
    )
    assert llm.calls
    assert result.model_name != "deterministic_identifier_renderer"
    assert result.diagnostics["deterministic_dispatch_bypassed"] is True
    assert result.diagnostics["deterministic_dispatch_bypass_reason"] == "conflicting_evidence"


def test_generate_bypasses_the_identifier_renderer_for_a_contested_retrieval_intent() -> None:
    """W2 (answering_flow_weakness_remediation_plan.md): the retrieval-side
    classification that selected this turn's evidence being an exact tie
    must route to the LLM even though the answer-side intent decision
    looks confident -- same request as the renderer-fires test above,
    except retrieval_intent_contested is now set."""
    llm = FakeLLMService(
        response='{"answer_text":"The retrieval intent for this question was ambiguous."}'
    )
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="list all serial and part nmubers",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            resolved_identifiers=[
                Identifier("id_part", "doc_001", raw_value="PN-001", identifier_type=IdentifierType.PART_NUMBER),
            ],
            retrieval_intent_contested=True,
        )
    )
    assert llm.calls
    assert result.model_name != "deterministic_identifier_renderer"
    assert result.diagnostics["deterministic_dispatch_bypassed"] is True
    assert result.diagnostics["deterministic_dispatch_bypass_reason"] == "retrieval_contested"


def test_generate_uses_deterministic_spare_parts_renderer_and_skips_llm() -> None:
    llm = FakeLLMService(response="No specific spare part list table was found.")
    service, _ = make_service(llm)
    chunk = RetrievedChunk(
        chunk_id="chunk_spare",
        document_id="doc_001",
        content="| Position No: | Qty: | Denomination: | Spare Part No: |\n|---|---|---|---|\n| 1 | 2 | Filter | A00103 |\n",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=["7 Components", "Spare Parts"],
        source=SourceLocation(page_start=45, page_end=46),
        citation=_make_citation("chunk_spare"),
    )
    result = service.generate(
        AnswerGenerationRequest(question="table of spare part list", context_chunks=[chunk])
    )
    assert result.answer_intent == AnswerIntent.TABLE_SUMMARY
    assert "Spare parts lists found:" in result.answer_text
    assert "no spare part" not in result.answer_text.lower()
    assert result.model_name == "deterministic_spare_parts_renderer"
    assert result.diagnostics["deterministic_renderer"] == "spare_parts_list_renderer"
    assert result.diagnostics["spare_parts_dropped_row_count"] == 0
    assert result.diagnostics["spare_parts_partial"] is False
    assert "spare_parts_table_parser_rules_version" in result.diagnostics
    assert llm.calls == []


def test_generate_diagnostics_include_formatting_layer_rules_versions() -> None:
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert "format_policy_rules_version" in result.diagnostics
    assert "key_value_extractor_rules_version" in result.diagnostics
    assert "maintenance_entry_merger_rules_version" in result.diagnostics


def test_generate_diagnostics_include_the_resolved_coverage_requirement() -> None:
    """PR 9 (answering_flow_weakness_remediation_plan.md): coverage_requirement
    must be computed during generation and surfaced through diagnostics, the
    same path reflection already reads answer_intent/dispatch info from."""
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(
            question="How do I replace the hydraulic filter?",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.PROCEDURE_STEPS,
        )
    )
    assert result.diagnostics["coverage_requirement"] == "ordered_procedure"


def test_generate_diagnostics_surface_format_policy_context_signals() -> None:
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    signals = result.diagnostics["format_policy_context_signals"]
    assert set(signals) == {
        "is_sparse_evidence",
        "has_low_confidence_evidence",
        "has_rich_structured_evidence",
        "has_table_rows",
        "has_entity_graph",
        "has_direct_maintenance_records",
        "has_exact_identifier_rows",
        "raw_source_dominant",
        "is_multi_document",
    }


def test_generate_passes_answer_generation_response_schema_to_llm() -> None:
    service, llm = make_service()
    service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert llm.calls
    assert llm.calls[0]["response_schema"] is not None
    assert "answer_text" in llm.calls[0]["response_schema"].get("properties", {})


class _CountingAnswerIntentAnalyzer(AnswerIntentAnalyzer):
    def __init__(self) -> None:
        super().__init__()
        self.call_count = 0

    def analyze(self, **kwargs):
        self.call_count += 1
        return super().analyze(**kwargs)


def test_generate_skips_recomputing_intent_when_decision_is_already_resolved() -> None:
    spy = _CountingAnswerIntentAnalyzer()
    service = AnswerGenerationService(
        llm_service=FakeLLMService(),
        answer_intent_analyzer=spy,
        answer_generation_model="qwen3:8b",
    )
    decision = AnswerIntentDecision(
        intent=AnswerIntent.SPECIFICATION_SUMMARY,
        confidence=0.9,
        reason="pre-resolved by workflow",
        matched_signals=["question:pressure"],
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="What is the pressure specification?",
            context_chunks=[_make_chunk(content="Test pressure: 700 bar")],
            answer_intent_decision=decision,
        )
    )
    assert spy.call_count == 0
    assert result.answer_intent == AnswerIntent.SPECIFICATION_SUMMARY
    assert result.confidence == 0.9


def test_generate_still_computes_intent_when_no_decision_is_provided() -> None:
    spy = _CountingAnswerIntentAnalyzer()
    service = AnswerGenerationService(
        llm_service=FakeLLMService(),
        answer_intent_analyzer=spy,
        answer_generation_model="qwen3:8b",
    )
    service.generate(
        AnswerGenerationRequest(
            question="What is the pressure specification?",
            context_chunks=[_make_chunk(content="Test pressure: 700 bar")],
        )
    )
    assert spy.call_count == 1


def test_generate_rejects_malformed_answer_generation_json() -> None:
    service, _ = make_service(FakeLLMService(response="The answer is 1000 hours."))
    with pytest.raises(
        SchemaValidationError,
        match="Malformed answer generation response JSON",
    ):
        service.generate(
            AnswerGenerationRequest(
                question="When to replace the filter?",
                context_chunks=[_make_chunk()],
            )
        )


# -- finding 3.3: compound-question gap for deterministic renderers --------


def test_generate_deterministic_identifier_renderer_sets_no_limitation_note_for_non_compound_question() -> None:
    llm = FakeLLMService(response="This answer should not be used.")
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="list all serial and part nmubers",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            resolved_identifiers=[
                Identifier(
                    "id_part",
                    "doc_001",
                    raw_value="PN-001",
                    identifier_type=IdentifierType.PART_NUMBER,
                ),
            ],
        )
    )
    assert result.limitation_note is None


def test_generate_bypasses_deterministic_identifier_renderer_for_a_compound_question() -> None:
    """Finding F3 (post-Phase-2 design): a compound question is no longer
    answered by the single-purpose deterministic renderer plus an
    after-the-fact disclaimer -- it routes to the full grounded LLM call
    instead, which can actually address both parts of the question."""
    llm = FakeLLMService(
        response='{"answer_text":"Part numbers: PN-001. To replace the pump, shut off power first."}'
    )
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="list all part numbers and how do i replace the pump",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            resolved_identifiers=[
                Identifier(
                    "id_part",
                    "doc_001",
                    raw_value="PN-001",
                    identifier_type=IdentifierType.PART_NUMBER,
                ),
            ],
        )
    )

    assert llm.calls
    assert result.model_name != "deterministic_identifier_renderer"
    assert result.limitation_note is None
    assert result.diagnostics["deterministic_dispatch_bypassed"] is True
    assert result.diagnostics["deterministic_dispatch_bypass_reason"] == "compound_question"
    # The default chunk's content ("Replace hydraulic filter...") happens to
    # contain a PROCEDURE_STEPS term ("replace"), so the unrelated clause's
    # intent is plausibly covered by what retrieval already fetched (PR 6's
    # explicit logging requirement, not a coverage guarantee).
    assert result.diagnostics["compound_question_coverage_plausible"] is True


def test_generate_deterministic_spare_parts_renderer_sets_no_limitation_note_for_non_compound_question() -> None:
    llm = FakeLLMService(response="No specific spare part list table was found.")
    service, _ = make_service(llm)
    chunk = RetrievedChunk(
        chunk_id="chunk_spare",
        document_id="doc_001",
        content="| Position No: | Qty: | Denomination: | Spare Part No: |\n|---|---|---|---|\n| 1 | 2 | Filter | A00103 |\n",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=["7 Components", "Spare Parts"],
        source=SourceLocation(page_start=45, page_end=46),
        citation=_make_citation("chunk_spare"),
    )
    result = service.generate(
        AnswerGenerationRequest(question="table of spare part list", context_chunks=[chunk])
    )
    assert result.limitation_note is None


def test_generate_bypasses_deterministic_spare_parts_renderer_for_a_compound_question() -> None:
    """Same rationale as the identifier-renderer case above, for the
    spare-parts renderer."""
    llm = FakeLLMService(
        response='{"answer_text":"Spare part A00103 (Filter). To replace the seal, drain the housing first."}'
    )
    service, _ = make_service(llm)
    chunk = RetrievedChunk(
        chunk_id="chunk_spare",
        document_id="doc_001",
        content="| Position No: | Qty: | Denomination: | Spare Part No: |\n|---|---|---|---|\n| 1 | 2 | Filter | A00103 |\n",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=["7 Components", "Spare Parts"],
        source=SourceLocation(page_start=45, page_end=46),
        citation=_make_citation("chunk_spare"),
    )

    result = service.generate(
        AnswerGenerationRequest(
            question="table of spare part list and how do i replace the seal",
            context_chunks=[chunk],
        )
    )

    assert llm.calls
    assert result.model_name != "deterministic_spare_parts_renderer"
    assert result.limitation_note is None
    assert result.diagnostics["deterministic_dispatch_bypassed"] is True
    assert result.diagnostics["deterministic_dispatch_bypass_reason"] == "compound_question"
    # The spare-parts table chunk's content carries no PROCEDURE_STEPS term
    # at all, so the unrelated ("how do i replace the seal") clause is NOT
    # plausibly covered by what retrieval fetched -- a genuine evidence gap.
    assert result.diagnostics["compound_question_coverage_plausible"] is False
