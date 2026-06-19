from src.application.workflows.extraction.prompt_builders import (
    ExtractionPromptBuilder,
)


def clone_chunk(sample_chunk, *, chunk_id: str, content: str):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=sample_chunk.chunk_type,
        section_path=sample_chunk.section_path,
        element_ids=sample_chunk.element_ids,
        table_ids=sample_chunk.table_ids,
        picture_ids=sample_chunk.picture_ids,
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )


def test_build_extraction_prompt_includes_document_and_chunk_context(
    sample_chunk,
) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="The spare part number is HP-001 and the manufacturer is Example Manufacturer.",
    )
    builder = ExtractionPromptBuilder()

    prompt = builder.build_extraction_prompt(
        sample_chunk.document_id,
        [sample_chunk, second_chunk],
    )

    assert sample_chunk.document_id in prompt
    assert sample_chunk.chunk_id in prompt
    assert second_chunk.chunk_id in prompt
    assert sample_chunk.content in prompt
    assert second_chunk.content in prompt
    assert "Maintenance Schedule" in prompt
    assert '"maintenance_tasks": [' in prompt
    assert '"spare_parts": [' in prompt
    assert '"equipment": [' in prompt
    assert '"manufacturers": [' in prompt
    assert "Return JSON only." in prompt
