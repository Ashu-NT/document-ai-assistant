from src.application.prompts.question_generation import (
    QUESTION_PROMPT_VERSION,
    QuestionPromptBuilder,
)


def test_question_prompt_builder_produces_deterministic_prompt(sample_chunk) -> None:
    builder = QuestionPromptBuilder()

    prompt = builder.build(sample_chunk, max_questions=5)

    assert builder.prompt_version == QUESTION_PROMPT_VERSION
    assert "Return questions only" in prompt
    assert "Maximum questions: 5" in prompt
    assert "Maintenance Schedule" in prompt
    assert sample_chunk.content in prompt


def test_question_prompt_version_is_exposed() -> None:
    assert QUESTION_PROMPT_VERSION == "v1"
