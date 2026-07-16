from src.application.workflows.classification.chunk_type_classification_workflow import (
    ChunkTypeClassificationWorkflow,
)
from src.domain.common import ChunkType
from src.shared.exceptions import SchemaValidationError


def clone_chunk(
    sample_chunk,
    *,
    chunk_id: str,
    content: str,
    chunk_type: ChunkType,
):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=chunk_type,
        section_path=list(sample_chunk.section_path),
        element_ids=list(sample_chunk.element_ids),
        table_ids=list(sample_chunk.table_ids),
        picture_ids=list(sample_chunk.picture_ids),
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )


def test_classify_unresolved_chunks_skips_schema_failures_and_continues(
    sample_chunk,
) -> None:
    first_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_failure",
        content="This chunk will trigger a malformed structured response.",
        chunk_type=ChunkType.GENERAL,
    )
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_success",
        content="Probable cause: low oil pressure. Remedy: inspect the line.",
        chunk_type=ChunkType.UNKNOWN,
    )
    workflow = ChunkTypeClassificationWorkflow(
        llm_service=object(),
        enable_chunk_type_classification=True,
    )

    def fake_classify(*, content: str | None, section_path: list[str]) -> ChunkType | None:
        assert section_path == ["Maintenance Schedule"]
        if content is not None and "malformed structured response" in content:
            raise SchemaValidationError("Classification response failed schema validation.")
        return ChunkType.TROUBLESHOOTING

    workflow.llm_classifier.classify = fake_classify
    progress_messages: list[str] = []

    reclassified = workflow.classify_unresolved_chunks(
        [first_chunk, second_chunk],
        progress_callback=progress_messages.append,
    )

    assert reclassified == 1
    assert first_chunk.chunk_type == ChunkType.GENERAL
    assert second_chunk.chunk_type == ChunkType.TROUBLESHOOTING
    assert second_chunk.chunk_type_source == "llm"
    assert any(
        "skipped 1 chunk(s) after llm/schema failures" in message.lower()
        for message in progress_messages
    )
    assert any(
        "LLM reclassified 1/2 chunk(s); skipped 1 failed chunk(s)." in message
        for message in progress_messages
    )
