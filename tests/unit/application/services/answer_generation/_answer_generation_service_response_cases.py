import pytest

from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation import AnswerIntent
from src.domain.common import ChunkType, IdentifierType
from src.domain.document.entities.identifier import Identifier

from tests.unit.application.services.answer_generation._answer_generation_service_support import (
    FakeLLMService,
    _make_chunk,
    _make_table_chunk,
    make_service,
)


def test_generate_returns_llm_output_as_answer_text() -> None:
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert result.answer_text == "The answer is 1000 hours."
    assert result.raw_model_output == '{"answer_text":"The answer is 1000 hours."}'
    assert result.limitation_note is None


def test_generate_surfaces_limitation_note_from_llm_response() -> None:
    service, _ = make_service(
        FakeLLMService(
            response=(
                '{"answer_text":"The filter is replaced every 1000 hours.",'
                '"limitation_note":"Only the primary filter interval was found; '
                'no secondary filter schedule was present in the sources."}'
            )
        )
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert result.answer_text == "The filter is replaced every 1000 hours."
    assert result.limitation_note == (
        "Only the primary filter interval was found; no secondary filter "
        "schedule was present in the sources."
    )


def test_generate_surfaces_sections_and_reference_notes_from_llm_response() -> None:
    service, _ = make_service(
        FakeLLMService(
            response=(
                '{"answer_text":"The filter is replaced every 1000 hours.",'
                '"sections":[{"heading":"Maintenance interval","body":'
                '"Replace every 1000 hours.","reference_note_ids":["r1"]}],'
                '"reference_notes":[{"note_id":"r1","claim_text":'
                '"Replace every 1000 operating hours.","source_number":1}]}'
            )
        )
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk(chunk_id="chunk_001")],
        )
    )
    assert len(result.sections) == 1
    assert result.sections[0].heading == "Maintenance interval"
    assert result.sections[0].reference_note_ids == ["r1"]
    assert len(result.reference_notes) == 1
    assert result.reference_notes[0].note_id == "r1"
    assert result.reference_notes[0].source_number == 1


def test_generate_resolves_reference_note_source_number_to_chunk_id() -> None:
    service, _ = make_service(
        FakeLLMService(
            response=(
                '{"answer_text":"Answer.","reference_notes":'
                '[{"note_id":"r1","claim_text":"claim","source_number":2}]}'
            )
        )
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="Question?",
            context_chunks=[_make_chunk("chunk_001"), _make_chunk("chunk_002")],
        )
    )
    assert result.reference_notes[0].source_number == 2
    assert result.reference_notes[0].chunk_id == "chunk_002"


def test_generate_leaves_chunk_id_none_for_unresolvable_source_number() -> None:
    service, _ = make_service(
        FakeLLMService(
            response=(
                '{"answer_text":"Answer.","reference_notes":'
                '[{"note_id":"r1","claim_text":"claim","source_number":99}]}'
            )
        )
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="Question?",
            context_chunks=[_make_chunk(chunk_id="chunk_001")],
        )
    )
    assert result.reference_notes[0].chunk_id is None


def test_generate_leaves_chunk_id_none_when_source_was_excluded_from_raw_appendix() -> None:
    """Finding 2.3: the structured JSON payload lists every retrieved
    source's source_number regardless of whether the raw-prose appendix
    budget actually included it as readable text. A citation naming a
    source_number that exists in the retrieval set, but was truncated away
    by RawSourceInclusionPolicy's budget, must resolve to chunk_id=None
    (unresolved) rather than a chunk_id the model never actually saw."""
    llm = FakeLLMService(
        response=(
            '{"answer_text":"Answer.","reference_notes":'
            '[{"note_id":"r1","claim_text":"claim","source_number":3}]}'
        )
    )
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="Show the specification table",
            context_chunks=[
                _make_table_chunk(
                    chunk_id="chunk_table",
                    chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                    content="Test pressure and design pressure values.",
                    section_path=["Certificate", "Particulars"],
                    page_start=5,
                    page_end=5,
                    metadata={
                        "table_rows_json": '[["Parameter","Value"],["Test pressure","700 bar"]]'
                    },
                ),
                _make_table_chunk(
                    chunk_id="chunk_supporting",
                    chunk_type=ChunkType.GENERAL,
                    content="The certificate particulars summarize the main ratings.",
                    section_path=["Certificate", "Particulars"],
                    page_start=5,
                    page_end=5,
                ),
                _make_table_chunk(
                    chunk_id="chunk_context",
                    chunk_type=ChunkType.OVERVIEW,
                    content="Overview context that should be deprioritized in the appendix.",
                    section_path=["Certificate", "Overview"],
                    page_start=4,
                    page_end=4,
                ),
            ],
            answer_intent=AnswerIntent.TABLE_SUMMARY,
        )
    )
    # SOURCE 3 exists in the retrieval set (and in the JSON payload's
    # metadata) but is dropped from the raw appendix by the table-heavy
    # budget (max 2 sources) -- see
    # test_generate_real_prompt_builder_emits_topology_tables_and_budgeted_appendix.
    assert result.reference_notes[0].source_number == 3
    assert result.reference_notes[0].chunk_id is None


def test_generate_deterministic_renderer_paths_have_empty_sections_and_reference_notes() -> None:
    llm = FakeLLMService(response="This answer should not be used.")
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="list all serial and part nmubers",
            context_chunks=[_make_chunk()],
            answer_intent=AnswerIntent.IDENTIFIER_LOOKUP,
            resolved_identifiers=[
                Identifier(
                    identifier_id="id_part",
                    document_id="doc_001",
                    raw_value="PN-001",
                    identifier_type=IdentifierType.PART_NUMBER,
                )
            ],
        )
    )
    assert result.sections == []
    assert result.reference_notes == []
    assert llm.calls == []


# -- finding 3.1: retry-with-repair on malformed/schema-invalid LLM JSON ----


def test_generate_repairs_trailing_comma_json_without_a_second_llm_call() -> None:
    llm = FakeLLMService(response='{"answer_text": "Fixed answer.",}')
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert result.answer_text == "Fixed answer."
    assert len(llm.calls) == 1


def test_generate_retries_once_with_corrective_note_and_succeeds() -> None:
    llm = FakeLLMService(
        responses=[
            "not json at all",
            '{"answer_text":"Recovered answer."}',
        ]
    )
    service, _ = make_service(llm)
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert result.answer_text == "Recovered answer."
    assert len(llm.calls) == 2
    assert llm.calls[0]["prompt"] != llm.calls[1]["prompt"]
    assert llm.calls[0]["prompt"] in llm.calls[1]["prompt"]
    assert "previous response was rejected" in llm.calls[1]["prompt"]


def test_generate_still_raises_schema_validation_error_after_exhausting_retries() -> None:
    from src.shared.exceptions import SchemaValidationError

    llm = FakeLLMService(response="not json at all, still not json on retry")
    service, _ = make_service(llm)
    with pytest.raises(SchemaValidationError, match="Malformed answer generation response JSON"):
        service.generate(
            AnswerGenerationRequest(
                question="When to replace the filter?",
                context_chunks=[_make_chunk()],
            )
        )
    assert len(llm.calls) == 2


# -- finding 3.2: explicit temperature/num_ctx for answer generation -------


def test_generate_passes_configured_temperature_and_num_ctx_to_llm_service() -> None:
    llm = FakeLLMService()
    service, _ = make_service(llm)
    service.answer_generation_temperature = 0.2
    service.answer_generation_num_ctx = 8192
    service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert llm.calls[0]["temperature"] == 0.2
    assert llm.calls[0]["num_ctx"] == 8192


def test_generate_uses_custom_temperature_and_num_ctx_from_constructor() -> None:
    from src.application.services.answer_generation.answer_generation_service import (
        AnswerGenerationService,
    )

    llm = FakeLLMService()
    service = AnswerGenerationService(
        llm_service=llm,
        answer_generation_model="qwen3:8b",
        answer_generation_temperature=0.7,
        answer_generation_num_ctx=4096,
    )
    service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert llm.calls[0]["temperature"] == 0.7
    assert llm.calls[0]["num_ctx"] == 4096


# -- finding 3.5: optional prompt-text capture in diagnostics ---------------


def test_generate_does_not_capture_prompt_text_by_default() -> None:
    service, _ = make_service()
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert "prompt_text" not in result.diagnostics


def test_generate_captures_prompt_text_when_setting_enabled() -> None:
    from src.application.services.answer_generation.answer_generation_service import (
        AnswerGenerationService,
    )

    llm = FakeLLMService()
    service = AnswerGenerationService(
        llm_service=llm,
        answer_generation_model="qwen3:8b",
        capture_answer_prompt_text=True,
    )
    result = service.generate(
        AnswerGenerationRequest(
            question="When to replace the filter?",
            context_chunks=[_make_chunk()],
        )
    )
    assert "prompt_text" in result.diagnostics
    assert result.diagnostics["prompt_text"] == llm.calls[0]["prompt"]
