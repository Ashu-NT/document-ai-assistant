from src.application.workflows.classification.prompt_builders import (
    ClassificationPromptBuilder,
)


def test_build_document_classification_prompt_includes_document_metadata(
    sample_document_graph,
) -> None:
    builder = ClassificationPromptBuilder()

    prompt = builder.build_document_classification_prompt(sample_document_graph)

    assert sample_document_graph.document.document_id in prompt
    assert sample_document_graph.document.file_name in prompt
    assert sample_document_graph.document.file_path in prompt
    assert sample_document_graph.document.title in prompt
    assert "Graph-derived content summary:" in prompt
    assert "Maintenance Schedule" in prompt
    assert "Replace hydraulic filter every 1000 operating hours." in prompt
    assert "Spare parts table" in prompt
    assert "Exploded view of hydraulic pump" in prompt
    assert '"label": "<document type>"' in prompt
    assert '"confidence_score": <float between 0 and 1>' in prompt
    assert "Allowed labels: manual" in prompt
    assert "Return JSON only." in prompt


def test_build_document_classification_prompt_supports_document_only_input(
    sample_document,
) -> None:
    builder = ClassificationPromptBuilder()

    prompt = builder.build_document_classification_prompt(sample_document)

    assert sample_document.document_id in prompt
    assert sample_document.title in prompt
    assert "No graph-derived content summary was available." in prompt


def test_build_chunk_classification_prompt_includes_chunk_context(
    sample_chunk,
) -> None:
    builder = ClassificationPromptBuilder()

    prompt = builder.build_chunk_classification_prompt(sample_chunk)

    assert sample_chunk.chunk_id in prompt
    assert sample_chunk.document_id in prompt
    assert sample_chunk.content in prompt
    assert "Maintenance Schedule" in prompt
    assert "Source pages: 10" in prompt
    assert '"label": "<chunk type>"' in prompt
    assert "Allowed labels: overview" in prompt
    assert "Return JSON only." in prompt
