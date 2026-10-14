from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.extraction.builders.equipment_info_builder import (
    EquipmentInfoBuilder,
)
from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.domain.extraction import ExtractionResult
from src.shared.ids import IdGenerator


def _chunk(chunk_id: str, content: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=ChunkType.GENERAL,
        source=SourceLocation(page_start=1, page_end=1),
    )


def _make_builder() -> EquipmentInfoBuilder:
    support = ExtractionBuilderSupport(
        confidence_threshold=0.5, require_human_review_default=False
    )
    return EquipmentInfoBuilder(IdGenerator(), support)


def test_correctly_separated_name_and_model_are_accepted_as_is() -> None:
    builder = _make_builder()
    chunk = _chunk("chunk_a", "Marine engine-generator set with 20V4000M53B engine.")

    entity = builder.build(
        {
            "name": "Marine engine-generator set",
            "model_number": "20V4000M53B",
            "source_chunk_id": "chunk_a",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_a": chunk},
        default_source_chunk_id="chunk_a",
        default_confidence=0.9,
    )

    assert entity.name == "Marine engine-generator set"
    assert entity.model_number == "20V4000M53B"
    assert entity.requires_human_review is False


def test_legitimate_compound_name_containing_a_model_like_token_is_preserved() -> None:
    builder = _make_builder()
    chunk = _chunk("chunk_a", "The Model R250 Pump is installed in bay 3.")

    entity = builder.build(
        {"name": "Model R250 Pump", "model_number": None, "source_chunk_id": "chunk_a"},
        document_id="doc_001",
        chunk_lookup={"chunk_a": chunk},
        default_source_chunk_id="chunk_a",
        default_confidence=0.9,
    )

    assert entity.name == "Model R250 Pump"
    assert entity.model_number is None
    assert entity.requires_human_review is False


def test_valid_source_chunk_with_supporting_text_is_not_flagged() -> None:
    builder = _make_builder()
    chunk = _chunk("chunk_a", "Marine engine-generator set with 20V4000M53B engine.")

    entity = builder.build(
        {
            "name": "Marine engine-generator set",
            "model_number": "20V4000M53B",
            "source_chunk_id": "chunk_a",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_a": chunk},
        default_source_chunk_id="chunk_a",
        default_confidence=0.9,
    )

    assert entity.source_chunk_id == "chunk_a"
    assert entity.requires_human_review is False


def test_valid_source_chunk_without_supporting_text_is_flagged() -> None:
    builder = _make_builder()
    chunk = _chunk("chunk_a", "Functional Description Maintenance Operating Instructions.")

    entity = builder.build(
        {
            "name": "Marine engine-generator set",
            "model_number": "20V4000M53B",
            "source_chunk_id": "chunk_a",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_a": chunk},
        default_source_chunk_id="chunk_a",
        default_confidence=0.9,
    )

    assert entity.source_chunk_id == "chunk_a"
    assert entity.requires_human_review is True


def test_evidence_in_a_different_chunk_is_flagged_not_silently_reassigned() -> None:
    builder = _make_builder()
    wrong_chunk = _chunk("chunk_wrong", "Functional Description Maintenance.")
    right_chunk = _chunk("chunk_right", "Marine engine-generator set with 20V4000M53B engine.")
    support = builder._support

    entity = builder.build(
        {
            "name": "Marine engine-generator set",
            "model_number": "20V4000M53B",
            "source_chunk_id": "chunk_wrong",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_wrong": wrong_chunk, "chunk_right": right_chunk},
        default_source_chunk_id="chunk_wrong",
        default_confidence=0.9,
    )

    # Flagged for review, but never silently rewritten to the chunk that
    # would actually support it - no "guess a better chunk" behavior.
    assert entity.source_chunk_id == "chunk_wrong"
    assert entity.requires_human_review is True
    assert support.equipment_unsupported_evidence_events == [
        {
            "source_chunk_id": "chunk_wrong",
            "model_number": "20V4000M53B",
            "serial_number": None,
        }
    ]


def test_ambiguous_candidate_chunks_never_trigger_automatic_reassignment() -> None:
    builder = _make_builder()
    cited_chunk = _chunk("chunk_cited", "General overview page.")
    other_supporting_chunk = _chunk(
        "chunk_other", "Compressor Model XJ900KL installed here."
    )

    entity = builder.build(
        {
            "name": "Compressor",
            "model_number": "XJ900KL",
            "source_chunk_id": "chunk_cited",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_cited": cited_chunk, "chunk_other": other_supporting_chunk},
        default_source_chunk_id="chunk_cited",
        default_confidence=0.9,
    )

    assert entity.source_chunk_id == "chunk_cited"
    assert entity.requires_human_review is True


def test_missing_source_chunk_id_falls_back_to_default_and_is_still_grounded() -> None:
    builder = _make_builder()
    chunk = _chunk("chunk_a", "Compressor Model XJ900KL installed here.")

    entity = builder.build(
        {"name": "Compressor", "model_number": "XJ900KL"},
        document_id="doc_001",
        chunk_lookup={"chunk_a": chunk},
        default_source_chunk_id="chunk_a",
        default_confidence=0.9,
    )

    assert entity.source_chunk_id == "chunk_a"
    assert entity.requires_human_review is False


def test_missing_source_chunk_id_falls_back_to_an_unsupporting_default_is_flagged() -> None:
    builder = _make_builder()
    chunk = _chunk("chunk_a", "Unrelated content.")

    entity = builder.build(
        {"name": "Compressor", "model_number": "XJ900KL"},
        document_id="doc_001",
        chunk_lookup={"chunk_a": chunk},
        default_source_chunk_id="chunk_a",
        default_confidence=0.9,
    )

    assert entity.source_chunk_id == "chunk_a"
    assert entity.requires_human_review is True


def test_invalid_source_chunk_id_still_flags_via_existing_mechanism() -> None:
    builder = _make_builder()
    chunk = _chunk("chunk_a", "Compressor Model XJ900KL installed here.")

    entity = builder.build(
        {
            "name": "Compressor",
            "model_number": "XJ900KL",
            "source_chunk_id": "chunk_does_not_exist",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_a": chunk},
        default_source_chunk_id="chunk_a",
        default_confidence=0.9,
    )

    assert entity.source_chunk_id == "chunk_a"
    assert entity.requires_human_review is True


def test_existing_extraction_result_validator_accepts_grounded_equipment() -> None:
    builder = _make_builder()
    chunk = _chunk("chunk_a", "Marine engine-generator set with 20V4000M53B engine.")
    entity = builder.build(
        {
            "name": "Marine engine-generator set",
            "model_number": "20V4000M53B",
            "source_chunk_id": "chunk_a",
        },
        document_id="doc_001",
        chunk_lookup={"chunk_a": chunk},
        default_source_chunk_id="chunk_a",
        default_confidence=0.9,
    )
    result = ExtractionResult(
        extraction_id="ext_1", document_id="doc_001", equipment=[entity]
    )

    validation = ExtractionResultValidator().validate(result)

    assert validation.is_valid
