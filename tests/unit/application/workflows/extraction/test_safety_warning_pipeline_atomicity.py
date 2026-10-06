import json

from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.response import ExtractionResponseParser
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.shared.ids import IdGenerator

# These tests prove the PARSER/BUILDER layer (as opposed to prompt guidance)
# already faithfully preserves whatever atomicity the model's response
# represents: N distinct response items -> N entities, one multi-sentence
# response item -> one entity. This is what rules mechanisms B/C out as the
# cause of the crushing-warning regression -- the merging happened before
# the response reached this layer (in model generation), not here.


def _make_chunk(chunk_id: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content="Safety notes.",
        chunk_type=ChunkType.SAFETY_WARNING,
        section_path=["Safety"],
        source=SourceLocation(page_start=163, page_end=163),
    )


def _make_assembler() -> ExtractionResultAssembler:
    support = ExtractionBuilderSupport(
        confidence_threshold=0.5, require_human_review_default=False
    )
    return ExtractionResultAssembler(
        id_generator=IdGenerator(),
        response_parser=ExtractionResponseParser(),
        support=support,
    )


def test_three_structurally_distinct_warnings_in_the_response_yield_three_entities() -> None:
    chunk = _make_chunk("c1")
    response = json.dumps(
        {
            "confidence_score": 0.9,
            "safety_warnings": [
                {
                    "warning_type": "warning",
                    "message": "Components are moving or rotating. Risk of crushing, danger of parts of the body being caught or pulled in!",
                    "source_chunk_id": "c1",
                },
                {
                    "warning_type": "warning",
                    "message": "Fuels are combustible and explosive. Risk of fire and explosion!",
                    "source_chunk_id": "c1",
                },
                {
                    "warning_type": "warning",
                    "message": "Hot components/surfaces. Risk of burns!",
                    "source_chunk_id": "c1",
                },
            ],
        }
    )

    result = _make_assembler().build("doc_001", [chunk], response)

    assert len(result.safety_warnings) == 3
    messages = {warning.message for warning in result.safety_warnings}
    assert "crushing" in " ".join(messages).lower()
    assert "fire and explosion" in " ".join(messages).lower()
    assert "risk of burns" in " ".join(messages).lower()


def test_one_coherent_multi_sentence_warning_stays_one_entity() -> None:
    chunk = _make_chunk("c1")
    message = (
        "Depressurize the hydraulic line before removing the filter housing. "
        "Failure to do so may result in injury from pressurized fluid escaping "
        "under high pressure."
    )
    response = json.dumps(
        {
            "confidence_score": 0.9,
            "safety_warnings": [
                {
                    "warning_type": "danger",
                    "message": message,
                    "source_chunk_id": "c1",
                }
            ],
        }
    )

    result = _make_assembler().build("doc_001", [chunk], response)

    assert len(result.safety_warnings) == 1
    # Sanitization may trim a trailing period - not an atomicity concern,
    # only exact equality up to that trim matters here.
    assert result.safety_warnings[0].message.rstrip(".") == message.rstrip(".")


def test_existing_safety_warning_parsing_and_building_remains_compatible() -> None:
    # Unchanged shape/aliases (component/confidence/requires_review) still work.
    chunk = _make_chunk("c1")
    response = json.dumps(
        {
            "confidence_score": 0.9,
            "requires_human_review": False,
            "safety_warnings": [
                {
                    "warning_type": "caution",
                    "message": "Wear hearing protection near the running engine.",
                    "component": "Engine",
                    "chunk_id": "c1",
                    "confidence": 0.85,
                    "requires_review": False,
                }
            ],
        }
    )

    result = _make_assembler().build("doc_001", [chunk], response)

    assert len(result.safety_warnings) == 1
    warning = result.safety_warnings[0]
    assert warning.warning_type == "caution"
    assert warning.component_name == "Engine"
    assert warning.source_chunk_id == "c1"
    assert warning.confidence_score == 0.85
