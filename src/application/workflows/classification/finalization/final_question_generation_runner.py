from typing import Callable

from src.application.services.question_generation import QuestionGenerationService
from src.domain.common import ChunkType
from src.domain.document import DocumentGraph
from src.shared.activity import ActivityContext
from src.shared.progress import emit_progress


class FinalQuestionGenerationRunner:
    """Generates questions for the final chunk set after post-classification
    finalization, honoring the workflow-level enable/disable default plus a
    per-call override, and always leaving the graph's question set in a
    well-defined state (empty when disabled)."""

    def __init__(
        self,
        *,
        question_generation_service: QuestionGenerationService,
        enable_question_generation: bool,
    ) -> None:
        self.question_generation_service = question_generation_service
        self.enable_question_generation = enable_question_generation

    def generate_if_enabled(
        self,
        *,
        graph: DocumentGraph,
        max_questions_per_chunk: int,
        enable_question_generation: bool | None = None,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        resolved_enable_question_generation = (
            self.enable_question_generation
            if enable_question_generation is None
            else enable_question_generation
        )
        if not resolved_enable_question_generation:
            emit_progress(
                progress_callback,
                "Question generation disabled; skipping final chunk questions.",
            )
            graph.replace_questions([])
            return

        questionable_chunks = [
            chunk
            for chunk in graph.chunks.values()
            if chunk.chunk_type != ChunkType.OVERVIEW
        ]
        emit_progress(
            progress_callback,
            f"Generating questions for {len(questionable_chunks)} chunk(s)...",
        )
        graph.replace_questions(
            self.question_generation_service.generate_for_chunks(
                questionable_chunks,
                max_questions_per_chunk=max_questions_per_chunk,
                activity_context=activity_context,
                progress_callback=progress_callback,
            )
        )
        emit_progress(
            progress_callback,
            f"Generated {len(graph.questions)} question(s) for final chunk set.",
        )
