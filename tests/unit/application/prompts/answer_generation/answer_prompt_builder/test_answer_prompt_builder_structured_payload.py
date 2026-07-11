from src.application.prompts.answer_generation import AnswerPromptBuilder
from src.application.services.answer_generation import AnswerFormatPolicy, AnswerIntent
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    chunk_id: str = "chunk_001",
    content: str = "Test pressure: 700 bar\nDesign pressure: 350 bar\nSize: DN 8",
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["Certificate", "Particulars"],
        source=SourceLocation(page_start=5, page_end=5),
        metadata=metadata or {},
    )


def test_specification_prompt_includes_key_values_in_structured_payload() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk()
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[chunk],
    )
    request = AnswerGenerationRequest(
        question="specification",
        context_chunks=[chunk],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(
            AnswerIntent.SPECIFICATION_SUMMARY
        ),
    )

    prompt = builder.build(request)

    assert "Evidence schema:" in prompt
    assert '"key_values"' in prompt
    assert '"key": "Test pressure"' in prompt
    assert '"value": "700 bar"' in prompt
    assert '"key": "Design pressure"' in prompt
    assert '"value": "350 bar"' in prompt
    assert '"key": "Size"' in prompt
    assert '"value": "DN 8"' in prompt


def test_structured_payload_includes_table_rows_when_available() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk(
        metadata={
            "table_rows_json": '[["Parameter","Value"],["Test pressure","700 bar"]]'
        }
    )
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        chunks=[chunk],
    )
    request = AnswerGenerationRequest(
        question="specification",
        context_chunks=[chunk],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(
            AnswerIntent.SPECIFICATION_SUMMARY
        ),
    )

    prompt = builder.build(request)

    assert '"sources"' in prompt
    assert '"table_rows": [' in prompt
    assert '"Parameter"' in prompt
    assert '"Test pressure"' in prompt
    assert '"700 bar"' in prompt
