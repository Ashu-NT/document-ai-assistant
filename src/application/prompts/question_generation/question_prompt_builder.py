from src.application.prompts.common import PromptMetadata
from src.application.prompts.question_generation.question_prompt_version import (
    QUESTION_PROMPT_VERSION,
)
from src.domain.document import DocumentChunk


class QuestionPromptBuilder:
    prompt_version = QUESTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="question_generation",
        version=QUESTION_PROMPT_VERSION,
        task_type="question_generation",
        model_type="llm",
        description="Generate user-facing questions from a document chunk.",
    )

    def build(
        self,
        chunk: DocumentChunk,
        *,
        max_questions: int,
    ) -> str:
        section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"

        return (
            "You generate concise user questions from technical document excerpts.\n"
            "Return questions only, one per line.\n"
            "Do not include numbering, bullets, explanations, or extra text.\n"
            f"Maximum questions: {max_questions}\n"
            f"Section path: {section_path}\n"
            "Chunk content:\n"
            f"{chunk.content}"
        )
