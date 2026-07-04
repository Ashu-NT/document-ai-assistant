from src.application.prompts.classification import ChunkTypePromptBuilder
from src.domain.common import ChunkType


class ChunkTypeLLMClassifier:
    """Calls an LLM to determine ChunkType for a single piece of content.

    Used by ChunkTypeClassificationWorkflow and kept intentionally small:
    prompt building, structured generation, structured parsing, and enum mapping.

    Imports the classification response parser/schema lazily inside classify()
    rather than at module level: this module is imported both directly (by
    tests/callers reaching for ChunkTypeLLMClassifier) and transitively via
    src.application.workflows.classification's own package __init__ (which
    pulls in ChunkTypeClassificationWorkflow, which imports this module) —
    a module-level import back into that package creates a circular import
    whenever this module is the first one touched.
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
        if self._llm_service is None or not content or not content.strip():
            return None

        from src.application.workflows.classification.classification_response_parser import (
            ClassificationResponseParser,
        )
        from src.application.workflows.classification.classification_response_schema import (
            build_classification_response_json_schema,
        )

        prompt = self._prompt_builder.build(
            _WorkflowLocalChunk(
                content=content,
                section_path=section_path,
            )
        )
        response = self._llm_service.generate(
            prompt,
            model=self._model,
            response_schema=build_classification_response_json_schema(),
        )
        payload = ClassificationResponseParser().parse(response)
        return self._resolve_chunk_type(payload.label)

    @staticmethod
    def _resolve_chunk_type(label: str) -> ChunkType | None:
        normalized = label.strip().lower().replace(" ", "_").replace("-", "_")
        for chunk_type in ChunkType:
            if normalized in {chunk_type.value, chunk_type.name.lower()}:
                return (
                    None
                    if chunk_type in {ChunkType.GENERAL, ChunkType.UNKNOWN}
                    else chunk_type
                )
        return None


class _WorkflowLocalChunk:
    def __init__(self, *, content: str, section_path: list[str]) -> None:
        self.chunk_id = "llm_reclassification_candidate"
        self.document_id = "unknown"
        self.section_id = None
        self.section_path = section_path
        self.source = _WorkflowLocalSource()
        self.chunk_index = 1
        self.chunk_total = 1
        self.content = content


class _WorkflowLocalSource:
    page_start = None
    page_end = None
