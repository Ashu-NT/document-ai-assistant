import re
from typing import Callable

from src.application.prompts.question_generation import (
    QUESTION_PROMPT_VERSION,
    QuestionPromptBuilder,
)
from src.application.services.ai import LLMService
from src.domain.common import ModelProcessingMetadata
from src.domain.document import DocumentChunk, GeneratedQuestion
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator, IdPrefix

QUESTION_PREFIX_PATTERN = re.compile(r"^\s*(?:[-*]+|\d+[\.\)]|[A-Za-z]\))\s*")


def _default_question_generation_model() -> str | None:
    try:
        from src.config.settings import llm_settings

        return (
            llm_settings.question_generation_llm
            or llm_settings.general_llm
        )
    except Exception:
        return None


class QuestionGenerationService:
    def __init__(
        self,
        llm_service: LLMService,
        id_generator: IdGenerator,
        prompt_builder: QuestionPromptBuilder | None = None,
        question_generation_model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.id_generator = id_generator
        self.prompt_builder = prompt_builder or QuestionPromptBuilder()
        self.question_generation_model = (
            question_generation_model
            or _default_question_generation_model()
        )

    @tracked_action(
        action="question_generation.chunk_generated",
        entity_type="question",
        activity=True,
        audit=False,
        event=False,
    )
    def generate_for_chunk(
        self,
        chunk: DocumentChunk,
        max_questions: int = 5,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> list[GeneratedQuestion]:
        self._emit_progress(
            progress_callback,
            f"Generating questions for chunk {chunk.chunk_id}...",
        )
        questions = self._generate_questions_for_chunk(
            chunk,
            max_questions=max_questions,
        )
        self._emit_progress(
            progress_callback,
            f"Generated {len(questions)} question(s) for chunk {chunk.chunk_id}.",
        )
        return questions

    @tracked_action(
        action="question_generation.batch_generated",
        entity_type="question",
        activity=True,
        audit=False,
        event=False,
    )
    def generate_for_chunks(
        self,
        chunks: list[DocumentChunk],
        max_questions_per_chunk: int = 5,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> list[GeneratedQuestion]:
        if max_questions_per_chunk <= 0:
            return []

        questions: list[GeneratedQuestion] = []
        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks, start=1):
            self._emit_progress(
                progress_callback,
                (
                    f"[questions {index}/{total_chunks}] Generating questions "
                    f"for chunk {chunk.chunk_id}..."
                ),
            )
            chunk_questions = self._generate_questions_for_chunk(
                chunk,
                max_questions=max_questions_per_chunk,
            )
            questions.extend(chunk_questions)
            self._emit_progress(
                progress_callback,
                (
                    f"[questions {index}/{total_chunks}] Generated "
                    f"{len(chunk_questions)} question(s) for chunk {chunk.chunk_id}."
                ),
            )

        return questions

    def _generate_questions_for_chunk(
        self,
        chunk: DocumentChunk,
        *,
        max_questions: int,
    ) -> list[GeneratedQuestion]:
        if max_questions <= 0:
            return []

        prompt = self.prompt_builder.build(
            chunk,
            max_questions=max_questions,
        )

        response = self.llm_service.generate(
            prompt,
            model=self.question_generation_model,
        )

        question_texts = self._parse_questions(
            response,
            max_questions=max_questions,
        )

        return [
            self._build_question(
                chunk,
                question_text=question_text,
            )
            for question_text in question_texts
        ]

    def _build_question(
        self,
        chunk: DocumentChunk,
        *,
        question_text: str,
    ) -> GeneratedQuestion:
        model_name = self.question_generation_model or "default"
        prompt_version = getattr(
            self.prompt_builder,
            "prompt_version",
            QUESTION_PROMPT_VERSION,
        )

        return GeneratedQuestion(
            question_id=self.id_generator.new_id(IdPrefix.QUESTION),
            document_id=chunk.document_id,
            chunk_id=chunk.chunk_id,
            question=question_text,
            processing_metadata=ModelProcessingMetadata(
                model_name=model_name,
                model_type="question_generation",
                prompt_version=prompt_version,
            ),
        )

    @classmethod
    def _parse_questions(
        cls,
        response: str,
        *,
        max_questions: int,
    ) -> list[str]:
        questions: list[str] = []
        seen: set[str] = set()

        for raw_line in response.splitlines():
            question = QUESTION_PREFIX_PATTERN.sub("", raw_line).strip()
            question = question.strip('"').strip("'").strip()

            if not question or question in seen:
                continue

            seen.add(question)
            questions.append(question)

            if len(questions) >= max_questions:
                break

        return questions

    @staticmethod
    def _emit_progress(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)
