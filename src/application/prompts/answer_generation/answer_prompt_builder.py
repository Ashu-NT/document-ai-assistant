from typing import TYPE_CHECKING

from src.application.prompts.answer_generation.answer_prompt_version import (
    ANSWER_PROMPT_VERSION,
)
from src.application.prompts.common import (
    ANSWER_GROUNDING_RULES,
    PromptMetadata,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

if TYPE_CHECKING:
    from src.application.services.answer_generation.answer_generation_request import (
        AnswerGenerationRequest,
    )


class AnswerPromptBuilder:
    prompt_version = ANSWER_PROMPT_VERSION
    metadata = PromptMetadata(
        name="answer_generation",
        version=ANSWER_PROMPT_VERSION,
        task_type="answer_generation",
        model_type="llm",
        description="Grounded answer generation from retrieved document chunks.",
    )

    def build(self, request: "AnswerGenerationRequest") -> str:
        chunks = request.context_chunks
        if request.max_context_chunks is not None:
            chunks = chunks[: request.max_context_chunks]

        source_blocks = "\n\n".join(
            self._format_source_block(index + 1, chunk)
            for index, chunk in enumerate(chunks)
        )

        intent_note = ""
        if request.query_intent:
            intent_note = f"Query intent: {request.query_intent}\n"

        return (
            f"{ANSWER_GROUNDING_RULES}\n\n"
            f"{intent_note}"
            f"Question: {request.question}\n\n"
            f"{source_blocks}"
        )

    @staticmethod
    def _format_source_block(index: int, chunk: RetrievedChunk) -> str:
        section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"
        page_range = AnswerPromptBuilder._format_page_range(chunk)

        return (
            f"SOURCE {index}\n"
            f"Document: {chunk.document_id}\n"
            f"Section: {section_path}\n"
            f"Pages: {page_range}\n"
            "---\n"
            f"{chunk.content}"
        )

    @staticmethod
    def _format_page_range(chunk: RetrievedChunk) -> str:
        page_start = chunk.source.page_start
        page_end = chunk.source.page_end

        if page_start is None and page_end is None:
            return "N/A"
        if page_start == page_end:
            return str(page_start)
        if page_start is None:
            return str(page_end)
        if page_end is None:
            return str(page_start)
        return f"{page_start}-{page_end}"
