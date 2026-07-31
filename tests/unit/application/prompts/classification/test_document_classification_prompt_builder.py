from src.application.prompts.classification import (
    DOCUMENT_CLASSIFICATION_PROMPT_VERSION,
    DocumentClassificationPromptBuilder,
)
from src.config.settings import classification_settings


def test_document_classification_prompt_builder_includes_document_summary_and_labels(
    sample_document_graph,
) -> None:
    builder = DocumentClassificationPromptBuilder()

    prompt = builder.build(sample_document_graph)

    assert builder.prompt_version == DOCUMENT_CLASSIFICATION_PROMPT_VERSION
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
    assert "Allowed labels:" in prompt
    assert "manual" in prompt
    assert "Return JSON only." in prompt


def test_document_classification_prompt_builder_supports_document_only_input(
    sample_document,
) -> None:
    builder = DocumentClassificationPromptBuilder()

    prompt = builder.build(sample_document)

    assert sample_document.document_id in prompt
    assert sample_document.title in prompt
    assert "No graph-derived content summary was available." in prompt


def test_document_classification_prompt_builder_truncates_graph_summary(
    sample_document_graph,
    monkeypatch,
) -> None:
    monkeypatch.setattr(classification_settings, "max_text_length", 10)
    builder = DocumentClassificationPromptBuilder()

    prompt = builder.build(sample_document_graph)

    full_summary = builder.summary_builder.build(sample_document_graph)
    assert full_summary[:10] in prompt
    assert "Replace hydraulic filter every 1000 operating hours." not in prompt
