from dataclasses import replace

from src.application.prompts.answer_generation import (
    ANSWER_PROMPT_VERSION,
    AnswerPromptBuilder,
)
from src.application.services.answer_generation import AnswerFormatPolicy, AnswerIntent
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
    AnswerRelationship,
    AnswerStructuredEntity,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    chunk_id: str = "chunk_001",
    content: str = "Replace hydraulic filter every 1000 hours.",
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=["Maintenance Schedule"],
        source=SourceLocation(page_start=5, page_end=5),
    )


def test_answer_prompt_builder_produces_grounding_and_structured_evidence_sections() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk()
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[chunk],
    )
    request = AnswerGenerationRequest(
        question="When should I replace the hydraulic filter?",
        context_chunks=[chunk],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(
            AnswerIntent.MAINTENANCE_SUMMARY
        ),
    )

    prompt = builder.build(request)

    assert builder.prompt_version == ANSWER_PROMPT_VERSION
    assert "ONLY the provided sources" in prompt
    assert "Do not use outside knowledge" in prompt
    assert 'Return JSON only with this shape:' in prompt
    assert '"answer_text": "<grounded answer>"' in prompt
    assert "Question: When should I replace the hydraulic filter?" in prompt
    assert "Answer format policy:" in prompt
    assert "Evidence schema:" in prompt
    assert "Structured evidence payload:" in prompt
    assert '"maintenance_entries"' in prompt
    assert '"task": "Replace hydraulic filter"' in prompt
    assert '"interval": "every 1000 hours"' in prompt
    assert "Raw source appendix:" in prompt


def test_answer_prompt_builder_instructs_flagging_contradictory_evidence() -> None:
    builder = AnswerPromptBuilder()
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=[_make_chunk()],
        answer_intent=AnswerIntent.GENERAL,
        structured_context=None,
        format_policy=AnswerFormatPolicy.for_intent(AnswerIntent.GENERAL),
    )

    prompt = builder.build(request)

    assert "sources disagree" in prompt


def test_answer_prompt_builder_restates_question_near_the_end() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk()
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.GENERAL,
        chunks=[chunk],
    )
    question = "When should I replace the hydraulic filter?"
    request = AnswerGenerationRequest(
        question=question,
        context_chunks=[chunk],
        answer_intent=AnswerIntent.GENERAL,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(AnswerIntent.GENERAL),
    )

    prompt = builder.build(request)

    closing_reminder = f"Answer the question above using only the evidence shown: {question}"
    assert closing_reminder in prompt
    # The reminder must be the closing statement of the prompt, appearing
    # after the raw source appendix -- not just present anywhere.
    assert prompt.rfind(closing_reminder) > prompt.rfind("Raw source appendix:")


def test_answer_prompt_builder_omits_structured_sections_without_structured_context() -> None:
    builder = AnswerPromptBuilder()
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=[_make_chunk()],
        answer_intent=AnswerIntent.GENERAL,
        structured_context=None,
        format_policy=AnswerFormatPolicy.for_intent(AnswerIntent.GENERAL),
    )

    prompt = builder.build(request)

    assert "Evidence schema:" not in prompt
    assert "Structured evidence payload:" not in prompt
    assert "Raw source appendix:" not in prompt


def test_answer_prompt_builder_with_context_exposes_diagnostics_and_appendix_selection() -> None:
    """Finding 2.3/2.8: appendix_source_numbers (which sources were actually
    shown as raw prose) and the canonicalizer's diagnostics counters are
    computed during build() but were previously discarded once build() only
    returned the prompt string. `build_with_context()` returns the bundle
    carrying both directly, per call -- not cached on a `last_context_bundle`
    instance attribute (finding F10: that design was unscoped mutable state,
    a latent concurrency hazard under any future concurrent caller)."""
    builder = AnswerPromptBuilder()

    chunks = [
        _make_chunk(chunk_id="c1", content="Content A"),
        _make_chunk(chunk_id="c2", content="Content B"),
    ]
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.GENERAL,
        chunks=chunks,
    )
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=chunks,
        answer_intent=AnswerIntent.GENERAL,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(AnswerIntent.GENERAL),
    )

    prompt, bundle = builder.build_with_context(request)

    assert prompt
    assert bundle is not None
    assert bundle.appendix_source_numbers == [1, 2]
    assert "prompt_canonicalized_key_values_removed" in bundle.diagnostics
    assert "prompt_payload_sources_content_omitted" in bundle.diagnostics
    assert "prompt_payload_table_rows_removed" in bundle.diagnostics


def test_answer_prompt_builder_build_returns_only_the_prompt_string() -> None:
    """`build()` keeps its original, narrower contract (just the prompt
    text) for the many callers that only ever needed that -- `build_with_
    context()` is the opt-in for callers that also need the bundle."""
    builder = AnswerPromptBuilder()
    request = AnswerGenerationRequest(question="Test?", context_chunks=[])

    prompt = builder.build(request)

    assert isinstance(prompt, str)
    assert "Test?" in prompt


def test_answer_prompt_builder_includes_provided_sources_in_appendix() -> None:
    builder = AnswerPromptBuilder()
    chunks = [
        _make_chunk(chunk_id="c1", content="Content A"),
        _make_chunk(chunk_id="c2", content="Content B"),
    ]
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.GENERAL,
        chunks=chunks,
    )
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=chunks,
        answer_intent=AnswerIntent.GENERAL,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(AnswerIntent.GENERAL),
    )

    prompt = builder.build(request)

    assert "Raw source appendix:" in prompt
    assert "SOURCE 1" in prompt
    assert "SOURCE 2" in prompt
    assert "Content A" in prompt
    assert "Content B" in prompt
    assert "Section: Maintenance Schedule" in prompt


def test_answer_prompt_builder_describes_sections_and_reference_notes_shape() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk()
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.GENERAL,
        chunks=[chunk],
    )
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=[chunk],
        answer_intent=AnswerIntent.GENERAL,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(AnswerIntent.GENERAL),
    )

    prompt = builder.build(request)

    assert '"sections"' in prompt
    assert '"reference_notes"' in prompt
    assert '"reference_note_ids"' in prompt
    assert '"source_number"' in prompt
    assert "does not apply to it" in prompt


def test_answer_prompt_builder_instructs_against_leaking_entity_ids() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk()
    structured_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.GENERAL,
        chunks=[chunk],
    )
    request = AnswerGenerationRequest(
        question="Test?",
        context_chunks=[chunk],
        answer_intent=AnswerIntent.GENERAL,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(AnswerIntent.GENERAL),
    )

    prompt = builder.build(request)

    assert "entity IDs" in prompt
    assert "relationship types" in prompt


def test_answer_prompt_builder_serializes_structured_entities_and_relationships() -> None:
    builder = AnswerPromptBuilder()
    chunk = _make_chunk()
    base_context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.PROCEDURE_STEPS,
        chunks=[chunk],
    )
    structured_context = replace(
        base_context,
        structured_entities=[
            AnswerStructuredEntity(
                entity_type="maintenance_task",
                entity_id="task_001",
                fields={"title": "Replace hydraulic filter", "interval": "Every 500 hours"},
                relationships=[
                    AnswerRelationship(
                        relationship_type="task_uses_procedure",
                        direction="outgoing",
                        status="accepted",
                        target_entity_type="procedure",
                        target_entity_id="procedure_001",
                        target_entity_fields={
                            "title": "Replace hydraulic filter",
                            "steps": [
                                "Depressurize the line.",
                                "Remove the old filter.",
                            ],
                        },
                    )
                ],
            )
        ],
    )
    request = AnswerGenerationRequest(
        question="How do I replace the hydraulic filter?",
        context_chunks=[chunk],
        answer_intent=AnswerIntent.PROCEDURE_STEPS,
        structured_context=structured_context,
        format_policy=AnswerFormatPolicy.for_intent(AnswerIntent.PROCEDURE_STEPS),
    )

    prompt = builder.build(request)

    assert '"structured_entities"' in prompt
    assert '"entity_type": "maintenance_task"' in prompt
    assert '"entity_id": "task_001"' in prompt
    assert '"relationship_edges"' in prompt
    assert '"relationship_families"' in prompt
    assert '"relationship_type": "task_uses_procedure"' in prompt
    assert '"source_entity_id": "task_001"' in prompt
    assert '"target_entity_id": "procedure_001"' in prompt
    assert '"steps": [' in prompt
