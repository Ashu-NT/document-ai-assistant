from src.application.prompts.extraction import ExtractionPromptType
from src.application.prompts.extraction.candidate_router import (
    ExtractionCandidateRouterPromptBuilder,
)
from src.application.workflows.extraction.candidates.extraction_candidate_router_response_parser import (
    ExtractionCandidateRouterResponseParser,
)
from src.application.workflows.extraction.candidates.extraction_candidate_router_schema import (
    build_extraction_candidate_router_json_schema,
)
from src.domain.document import DocumentChunk
from src.shared.exceptions import SchemaValidationError


def _default_enabled() -> bool:
    try:
        from src.config.settings import extraction_settings

        return extraction_settings.extraction_candidate_router_enabled
    except Exception:
        return False


def _default_model() -> str | None:
    try:
        from src.config.settings import llm_settings

        return llm_settings.extraction_llm or llm_settings.general_llm
    except Exception:
        return None


class ExtractionCandidateLLMRouter:
    """
    Optional LLM fallback for chunks whose ChunkType stayed GENERAL/UNKNOWN
    even after ChunkTypeClassificationWorkflow's own LLM fallback. Instead
    of ExtractionCandidateSelector failing open to "ask about every entity
    type" for such chunks, this makes one targeted call asking the LLM
    directly which entity types are worth extracting from this specific
    chunk.

    Disabled by default (EXTRACTION_CANDIDATE_ROUTER_ENABLED=false): this
    adds an LLM call for every otherwise-unresolved chunk, which works
    against "don't spin up the LLM for irrelevant chunks" unless the
    narrower downstream prompts it enables save more than this call costs.
    """

    def __init__(
        self,
        *,
        llm_service=None,
        model: str | None = None,
        enabled: bool | None = None,
        prompt_builder: ExtractionCandidateRouterPromptBuilder | None = None,
    ) -> None:
        self._llm_service = llm_service
        self._model = model or _default_model()
        self._enabled = enabled if enabled is not None else _default_enabled()
        self._prompt_builder = prompt_builder or ExtractionCandidateRouterPromptBuilder()
        self._response_parser = ExtractionCandidateRouterResponseParser()

    def is_available(self) -> bool:
        return self._enabled and self._llm_service is not None

    def route(self, chunk: DocumentChunk) -> frozenset[ExtractionPromptType] | None:
        if not self.is_available():
            return None
        if not chunk.content or not chunk.content.strip():
            return None

        prompt = self._prompt_builder.build(chunk.content)
        response = self._llm_service.generate(
            prompt,
            model=self._model,
            response_schema=build_extraction_candidate_router_json_schema(),
        )
        try:
            payload = self._response_parser.parse(response)
        except SchemaValidationError:
            return None

        resolved = payload.resolved_types()
        return resolved or None
