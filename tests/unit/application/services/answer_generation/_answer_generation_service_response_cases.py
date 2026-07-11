import pytest

from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation import AnswerIntent
from src.domain.common import IdentifierType
from src.domain.document.entities.identifier import Identifier

from tests.unit.application.services.answer_generation._answer_generation_service_support import (
    FakeLLMService,
    _make_chunk,
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
