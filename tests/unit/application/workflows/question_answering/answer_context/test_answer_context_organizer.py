from src.application.services.answer_generation import AnswerIntent
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    *,
    chunk_id: str,
    content: str,
    chunk_type: ChunkType = ChunkType.TECHNICAL_SPECIFICATION,
    section_path: list[str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=chunk_type,
        section_path=section_path or ["Certificate", "Particulars"],
        source=SourceLocation(page_start=2, page_end=2),
    )


def test_context_organizer_extracts_spec_key_values_and_preserves_metadata() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[
            _make_chunk(
                chunk_id="chunk_001",
                content="Test pressure: 700 bar\nDesign pressure: 350 bar\nSize: DN 8",
            )
        ],
    )

    assert context.source_count == 1
    assert context.sources[0].source_number == 1
    assert context.sources[0].document_id == "doc_001"
    assert context.sources[0].page_start == 2
    assert context.sources[0].section_path == "Certificate > Particulars"
    assert context.sources[0].content.startswith("Test pressure")
    assert ("Test pressure", "700 bar") in {
        (item.key, item.value) for item in context.key_values
    }
    assert ("Design pressure", "350 bar") in {
        (item.key, item.value) for item in context.key_values
    }


def test_context_organizer_groups_sources_by_chunk_type_and_section() -> None:
    organizer = AnswerContextOrganizer()
    context = organizer.organize(
        answer_intent=AnswerIntent.PROCEDURE_STEPS,
        chunks=[
            _make_chunk(
                chunk_id="chunk_a",
                content="1. Stop the pump",
                chunk_type=ChunkType.OPERATION_INSTRUCTION,
                section_path=["Operation", "Stopping"],
            ),
            _make_chunk(
                chunk_id="chunk_b",
                content="2. Isolate the line",
                chunk_type=ChunkType.OPERATION_INSTRUCTION,
                section_path=["Operation", "Stopping"],
            ),
        ],
    )

    assert len(context.source_groups) == 1
    assert context.source_groups[0].chunk_type == "operation_instruction"
    assert len(context.section_groups) == 1
    assert context.section_groups[0].section_path == "Operation > Stopping"
