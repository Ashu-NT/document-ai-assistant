import re
from typing import Any

from src.application.services.ai import LLMService
from src.application.services.classification import ClassificationService
from src.application.validation.classification import DocumentClassificationValidator
from src.application.workflows.classification.classification_response_parser import (
    ClassificationResponseParser,
)
from src.application.workflows.classification.prompt_builders import (
    ClassificationPromptBuilder,
)
from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType, ModelProcessingMetadata
from src.domain.document import Document, DocumentGraph
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator, IdPrefix

KEY_PATTERN = re.compile(r"[^a-z0-9]+")


def _default_document_classification_model() -> str | None:
    try:
        from src.config.settings import classification_settings, llm_settings

        return (
            classification_settings.classification_llm
            or llm_settings.classification_llm
            or llm_settings.general_llm
        )
    except Exception:
        return None


class DocumentClassificationWorkflow:
    def __init__(
        self,
        llm_service: LLMService,
        classification_service: ClassificationService,
        document_classification_validator: DocumentClassificationValidator,
        id_generator: IdGenerator,
        prompt_builder: ClassificationPromptBuilder | None = None,
        classification_model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.classification_service = classification_service
        self.document_classification_validator = document_classification_validator
        self.id_generator = id_generator
        self.prompt_builder = prompt_builder or ClassificationPromptBuilder()
        self.classification_model = (
            classification_model
            or _default_document_classification_model()
        )
        self.response_parser = ClassificationResponseParser(
            label_aliases={"predicted_label", "document_type"},
        )

    @tracked_action(
        action="classification.document_generated",
        entity_type="document",
        activity=True,
        audit=False,
        event=False,
    )
    def classify_document(
        self,
        document_graph: DocumentGraph | Document,
        activity_context: ActivityContext | None = None,
    ) -> DocumentClassification:
        document = self._resolve_document(document_graph)
        prompt = self.prompt_builder.build_document_classification_prompt(
            document_graph
        )
        response = self.llm_service.generate(
            prompt,
            model=self.classification_model,
            activity_context=activity_context,
        )

        classification = self._build_classification(document, response)

        validation = self.document_classification_validator.validate(classification)
        validation.raise_if_invalid()

        self.classification_service.save_document_classification(
            classification,
            activity_context=activity_context,
        )
        return classification

    def _build_classification(
        self,
        document: Document,
        response: str,
    ) -> DocumentClassification:
        parsed = self.response_parser.parse(response)
        document_type = self._resolve_document_type(parsed["label"])
        metadata_errors = self._build_metadata_errors(parsed["label"], document_type)

        result = ClassificationResult(
            classification_id=self.id_generator.new_id(IdPrefix.CLASSIFICATION),
            document_id=document.document_id,
            predicted_label=document_type.value,
            confidence_score=parsed["confidence_score"],
            rationale=parsed["rationale"],
            evidence=parsed["evidence"],
            processing_metadata=ModelProcessingMetadata(
                model_name=self.classification_model or "default",
                model_type="document_classification",
                confidence=parsed["confidence_score"],
                prompt_version=getattr(
                    self.prompt_builder,
                    "document_prompt_version",
                    getattr(self.prompt_builder, "prompt_version", None),
                ),
                errors=metadata_errors,
            ),
        )

        return DocumentClassification(
            document_id=document.document_id,
            document_type=document_type,
            result=result,
        )

    @staticmethod
    def _resolve_document_type(label: str) -> DocumentType:
        normalized = KEY_PATTERN.sub("_", label.lower()).strip("_")

        for document_type in DocumentType:
            if normalized in {
                document_type.value,
                document_type.name.lower(),
            }:
                return document_type

        return DocumentType.UNKNOWN

    @staticmethod
    def _build_metadata_errors(
        raw_label: str,
        document_type: DocumentType,
    ) -> list[str]:
        normalized = KEY_PATTERN.sub("_", raw_label.lower()).strip("_")

        if document_type == DocumentType.UNKNOWN and normalized != DocumentType.UNKNOWN.value:
            return [f"Unknown label returned by model: {raw_label}"]

        return []

    @staticmethod
    def _resolve_document(document_graph: DocumentGraph | Document) -> Document:
        if isinstance(document_graph, DocumentGraph):
            return document_graph.document
        return document_graph
