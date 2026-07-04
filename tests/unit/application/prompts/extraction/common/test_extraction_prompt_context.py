from src.application.prompts.extraction.common import ExtractionPromptContext


def test_extraction_prompt_context_defaults_chunks_to_empty_list() -> None:
    context = ExtractionPromptContext(document_id="doc_001")

    assert context.chunks == []
    assert context.previous_error is None


def test_extraction_prompt_context_holds_chunks_and_previous_error(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id="doc_001",
        chunks=[sample_chunk],
        previous_error="bad schema",
    )

    assert context.chunks == [sample_chunk]
    assert context.previous_error == "bad schema"
