from src.application.prompts.answer_generation import (
    ANSWER_PROMPT_VERSION,
    AnswerPromptBuilder,
)
from src.application.services.ai.llm_service import LLMService
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_result import (
    GeneratedAnswer,
)
from src.domain.common.processing_metadata import ModelProcessingMetadata
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action


def _default_answer_generation_model() -> str | None:
    try:
        from src.config.settings import llm_settings

        return llm_settings.answer_generation_llm or llm_settings.general_llm
    except Exception:
        return None


class AnswerGenerationService:
    def __init__(
        self,
        llm_service: LLMService,
        prompt_builder: AnswerPromptBuilder | None = None,
        answer_generation_model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder or AnswerPromptBuilder()
        self.answer_generation_model = (
            answer_generation_model or _default_answer_generation_model()
        )

    @tracked_action(
        action="answer_generation.generated",
        entity_type="answer",
        activity=True,
        audit=False,
        event=False,
    )
    def generate(
        self,
        request: AnswerGenerationRequest,
        activity_context: ActivityContext | None = None,
    ) -> GeneratedAnswer:
        prompt = self.prompt_builder.build(request)
        prompt_version = getattr(
            self.prompt_builder,
            "prompt_version",
            ANSWER_PROMPT_VERSION,
        )

        raw_output = self.llm_service.generate(
            prompt,
            model=self.answer_generation_model,
        )

        citations, cited_chunk_ids = self._build_citations(request.context_chunks)

        model_name = self.answer_generation_model or "default"

        return GeneratedAnswer(
            answer_text=raw_output,
            citations=citations,
            cited_chunk_ids=cited_chunk_ids,
            prompt_version=prompt_version,
            model_name=model_name,
            raw_model_output=raw_output,
            metadata=ModelProcessingMetadata(
                model_name=model_name,
                model_type="answer_generation",
                prompt_version=prompt_version,
            ),
        )

    @staticmethod
    def _build_citations(
        chunks: list[RetrievedChunk],
    ) -> tuple[list[Citation], list[str]]:
        citations: list[Citation] = []
        cited_chunk_ids: list[str] = []
        for chunk in chunks:
            if chunk.citation is not None:
                citations.append(chunk.citation)
                cited_chunk_ids.append(chunk.chunk_id)
        return citations, cited_chunk_ids
