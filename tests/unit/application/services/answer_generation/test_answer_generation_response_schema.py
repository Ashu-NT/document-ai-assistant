import pytest
from pydantic import ValidationError

from src.application.services.answer_generation.answer_generation_response_schema import (
    AnswerGenerationResponsePayload,
    AnswerSectionPayload,
    ReferenceNotePayload,
)


def test_payload_parses_with_sections_and_reference_notes() -> None:
    payload = AnswerGenerationResponsePayload.model_validate(
        {
            "answer_text": "The filter must be replaced every 1000 hours.",
            "sections": [
                {
                    "heading": "Maintenance interval",
                    "body": "Replace the filter every 1000 operating hours.",
                    "reference_note_ids": ["r1"],
                }
            ],
            "reference_notes": [
                {
                    "note_id": "r1",
                    "claim_text": "Replace every 1000 operating hours.",
                    "source_number": 1,
                }
            ],
        }
    )

    assert payload.answer_text == "The filter must be replaced every 1000 hours."
    assert len(payload.sections) == 1
    assert payload.sections[0] == AnswerSectionPayload(
        heading="Maintenance interval",
        body="Replace the filter every 1000 operating hours.",
        reference_note_ids=["r1"],
    )
    assert len(payload.reference_notes) == 1
    assert payload.reference_notes[0] == ReferenceNotePayload(
        note_id="r1",
        claim_text="Replace every 1000 operating hours.",
        source_number=1,
    )


def test_payload_defaults_sections_and_reference_notes_to_empty() -> None:
    payload = AnswerGenerationResponsePayload.model_validate(
        {"answer_text": "Only the answer text was provided."}
    )

    assert payload.sections == []
    assert payload.reference_notes == []


def test_payload_still_rejects_unknown_top_level_keys() -> None:
    with pytest.raises(ValidationError):
        AnswerGenerationResponsePayload.model_validate(
            {"answer_text": "Answer.", "unexpected_field": "value"}
        )


@pytest.mark.parametrize(
    "field_name",
    ["note_id", "claim_text"],
)
def test_reference_note_payload_rejects_empty_strings(field_name: str) -> None:
    values = {
        "note_id": "r1",
        "claim_text": "A claim.",
        "source_number": 1,
    }
    values[field_name] = ""

    with pytest.raises(ValidationError):
        ReferenceNotePayload.model_validate(values)


@pytest.mark.parametrize(
    "field_name",
    ["heading", "body"],
)
def test_answer_section_payload_rejects_empty_strings(field_name: str) -> None:
    values = {"heading": "Heading", "body": "Body text."}
    values[field_name] = ""

    with pytest.raises(ValidationError):
        AnswerSectionPayload.model_validate(values)


@pytest.mark.parametrize("source_number", [0, -1])
def test_reference_note_payload_rejects_non_positive_source_number(
    source_number: int,
) -> None:
    with pytest.raises(ValidationError):
        ReferenceNotePayload.model_validate(
            {
                "note_id": "r1",
                "claim_text": "A claim.",
                "source_number": source_number,
            }
        )


def test_answer_section_payload_defaults_reference_note_ids_to_empty() -> None:
    section = AnswerSectionPayload.model_validate(
        {"heading": "Heading", "body": "Body text."}
    )

    assert section.reference_note_ids == []
