from src.application.prompts.classification import (
    CHUNK_TYPE_PROMPT_VERSION,
    ChunkTypePromptBuilder,
)


def test_chunk_type_prompt_builder_includes_section_path_content_and_labels(
    sample_chunk,
) -> None:
    builder = ChunkTypePromptBuilder()

    prompt = builder.build(sample_chunk)

    assert builder.prompt_version == CHUNK_TYPE_PROMPT_VERSION
    assert sample_chunk.chunk_id in prompt
    assert sample_chunk.document_id in prompt
    assert sample_chunk.content in prompt
    assert "Maintenance Schedule" in prompt
    assert "Source pages: 10" in prompt
    assert '"label": "<chunk type>"' in prompt
    assert "Allowed labels:" in prompt
    assert "overview" in prompt
    assert "Return JSON only." in prompt


def test_chunk_type_prompt_builder_supports_reclassification_prompt(
    sample_chunk,
) -> None:
    builder = ChunkTypePromptBuilder()

    prompt = builder.build_reclassification_prompt(
        content=sample_chunk.content,
        section_path=sample_chunk.section_path,
    )

    assert "Reply with ONLY the type name" in prompt
    assert sample_chunk.content in prompt
    assert "Maintenance Schedule" in prompt
