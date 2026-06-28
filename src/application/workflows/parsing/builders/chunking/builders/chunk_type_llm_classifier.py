import re

from src.application.prompts.classification import ChunkTypePromptBuilder
from src.domain.common import ChunkType

_NORMALIZE = re.compile(r"[^a-z0-9]+")


def parse_chunk_type_response(response: str) -> ChunkType:
    normalized = _NORMALIZE.sub("_", response.strip().lower()).strip("_")
    for chunk_type in ChunkType:
        if normalized in {chunk_type.value, chunk_type.name.lower()}:
            return chunk_type
    first_word = normalized.split("_")[0] if "_" in normalized else normalized
    for chunk_type in ChunkType:
        if chunk_type.value.startswith(first_word) or chunk_type.name.lower().startswith(first_word):
            return chunk_type
    return ChunkType.GENERAL


class ChunkTypeLLMClassifier:
    """Calls an LLM to determine ChunkType for a single piece of content.

    Used by ChunkTypeClassificationWorkflow — not wired into ChunkTypeResolver.
    Stateless beyond the injected LLMService so it can be constructed once
    and called repeatedly without side effects.
    """

    def __init__(self, llm_service=None, model: str | None = None) -> None:
        self._llm_service = llm_service
        self._model = model
        self._prompt_builder = ChunkTypePromptBuilder()

    def is_available(self) -> bool:
        return self._llm_service is not None

    def classify(
        self,
        *,
        content: str | None,
        section_path: list[str],
    ) -> ChunkType | None:
        """Return a ChunkType, or None when unavailable or when LLM returns GENERAL."""
        if self._llm_service is None or not content or not content.strip():
            return None
        prompt = self._prompt_builder.build_reclassification_prompt(
            content=content,
            section_path=section_path,
        )
        try:
            response = self._llm_service.generate(prompt, model=self._model)
            result = parse_chunk_type_response(response or "")
            return result if result != ChunkType.GENERAL else None
        except Exception:
            return None
