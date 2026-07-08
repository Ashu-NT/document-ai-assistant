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
from src.application.workflows.classification.classification_response_schema import (
    build_classification_response_json_schema,
)
from src.application.workflows.classification.classification_shared import (
    build_unknown_label_errors,
    resolve_enum_label,
)
from src.domain.classification import ChunkClassification, ClassificationResult
from src.domain.common import ChunkType, ModelProcessingMetadata
from src.domain.document import DocumentChunk
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator, IdPrefix


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
        self.response_parser = ClassificationResponseParser()

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
            response_schema=build_classification_response_json_schema(),
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
        chunk_type = resolve_enum_label(parsed.label, ChunkType)
        metadata_errors = build_unknown_label_errors(parsed.label, chunk_type)

        result = ClassificationResult(
            classification_id=self.id_generator.new_id(IdPrefix.CLASSIFICATION),
            document_id=chunk.document_id,
            predicted_label=chunk_type.value,
            confidence_score=parsed.confidence_score,
            rationale=parsed.rationale,
            evidence=parsed.evidence,
            processing_metadata=ModelProcessingMetadata(
                model_name=self.classification_model or "default",
                model_type="chunk_classification",
                confidence=parsed.confidence_score,
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
