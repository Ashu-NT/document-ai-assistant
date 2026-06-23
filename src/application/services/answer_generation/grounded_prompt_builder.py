from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

_GROUNDING_RULES = (
    "You are a technical document assistant.\n"
    "Answer the question using ONLY the provided sources below.\n"
    "Rules:\n"
    "- Do not use outside knowledge.\n"
    "- Do not invent values, steps, part numbers, procedures, safety warnings, or recommendations.\n"
    "- If the sources do not contain enough information to answer, say so explicitly.\n"
    "- Cite the source numbers you used, e.g. [SOURCE 1] or [SOURCE 1][SOURCE 3].\n"
    "- Keep the answer concise and technical.\n"
    "- For safety, procedure, or maintenance questions: only provide steps and warnings "
    "that are explicitly present in the sources. Do not extrapolate."
)


class GroundedPromptBuilder:
    prompt_version = "v1"

    def build(self, request: AnswerGenerationRequest) -> str:
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
            f"{_GROUNDING_RULES}\n\n"
            f"{intent_note}"
            f"Question: {request.question}\n\n"
            f"{source_blocks}"
        )

    @staticmethod
    def _format_source_block(index: int, chunk: RetrievedChunk) -> str:
        section_path = (
            " > ".join(chunk.section_path) if chunk.section_path else "N/A"
        )
        page_range = GroundedPromptBuilder._format_page_range(chunk)

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
