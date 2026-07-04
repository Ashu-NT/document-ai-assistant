from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.procedures import (
    PROCEDURE_EXTRACTION_PROMPT_VERSION,
)


def test_procedure_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.PROCEDURE, context)

    assert result.prompt_version == PROCEDURE_EXTRACTION_PROMPT_VERSION
    assert '"procedures": [' in result.prompt_text
    assert '"steps"' in result.prompt_text
