import re
from typing import Any

from src.application.prompts.classification import (
    CHUNK_TYPE_PROMPT_VERSION,
    ChunkTypePromptBuilder,
)
from src.application.services.ai import LLMService
from src.application.services.classification import ClassificationService
from src.application.validation.classification import ChunkClassificationValidator
from src.application.workflows.classification.classification_response_parser import (
    ClassificationResponseParser,
)
from src.domain.classification import ChunkClassification, ClassificationResult
from src.domain.common import ChunkType, ModelProcessingMetadata
from src.domain.document import DocumentChunk
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator, IdPrefix

KEY_PATTERN = re.compile(r"[^a-z0-9]+")


def _default_chunk_classification_model() -> str | None:
    try:
        from src.config.settings import classification_settings, llm_settings

        return (
            classification_settings.chunk_classification_llm
            or classification_settings.classification_llm
            or llm_settings.classification_llm
            or llm_settings.general_llm
        )
    except Exception:
        return None


class ChunkClassificationWorkflow:
    def __init__(
        self,
        llm_service: LLMService,
        classification_service: ClassificationService,
        chunk_classification_validator: ChunkClassificationValidator,
        id_generator: IdGenerator,
        prompt_builder: ChunkTypePromptBuilder | None = None,
        classification_model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.classification_service = classification_service
        self.chunk_classification_validator = chunk_classification_validator
        self.id_generator = id_generator
        self.prompt_builder = prompt_builder or ChunkTypePromptBuilder()
        self.classification_model = (
            classification_model
            or _default_chunk_classification_model()
        )
        self.response_parser = ClassificationResponseParser(
            label_aliases={"predicted_label", "chunk_type"},
        )

    @tracked_action(
        action="classification.chunk_generated",
        entity_type="chunk",
        activity=True,
        audit=False,
        event=False,
    )
    def classify_chunk(
        self,
        chunk: DocumentChunk,
        activity_context: ActivityContext | None = None,
    ) -> ChunkClassification:
        prompt = self.prompt_builder.build(chunk)
        response = self.llm_service.generate(
            prompt,
            model=self.classification_model,
            activity_context=activity_context,
        )

        classification = self._build_classification(chunk, response)

        validation = self.chunk_classification_validator.validate(classification)
        validation.raise_if_invalid()

        self.classification_service.save_chunk_classification(
            classification,
            activity_context=activity_context,
        )
        return classification

    def _build_classification(
        self,
        chunk: DocumentChunk,
        response: str,
    ) -> ChunkClassification:
        parsed = self.response_parser.parse(response)
        chunk_type = self._resolve_chunk_type(parsed["label"])
        metadata_errors = self._build_metadata_errors(parsed["label"], chunk_type)

        result = ClassificationResult(
            classification_id=self.id_generator.new_id(IdPrefix.CLASSIFICATION),
            document_id=chunk.document_id,
            predicted_label=chunk_type.value,
            confidence_score=parsed["confidence_score"],
            rationale=parsed["rationale"],
            evidence=parsed["evidence"],
            processing_metadata=ModelProcessingMetadata(
                model_name=self.classification_model or "default",
                model_type="chunk_classification",
                confidence=parsed["confidence_score"],
                prompt_version=getattr(
                    self.prompt_builder,
                    "prompt_version",
                    CHUNK_TYPE_PROMPT_VERSION,
                ),
                errors=metadata_errors,
            ),
        )

        return ChunkClassification(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            chunk_type=chunk_type,
            result=result,
        )

    @staticmethod
    def _resolve_chunk_type(label: str) -> ChunkType:
        normalized = KEY_PATTERN.sub("_", label.lower()).strip("_")

        for chunk_type in ChunkType:
            if normalized in {
                chunk_type.value,
                chunk_type.name.lower(),
            }:
                return chunk_type

        return ChunkType.UNKNOWN

    @staticmethod
    def _build_metadata_errors(
        raw_label: str,
        chunk_type: ChunkType,
    ) -> list[str]:
        normalized = KEY_PATTERN.sub("_", raw_label.lower()).strip("_")

        if chunk_type == ChunkType.UNKNOWN and normalized != ChunkType.UNKNOWN.value:
            return [f"Unknown label returned by model: {raw_label}"]

        return []
