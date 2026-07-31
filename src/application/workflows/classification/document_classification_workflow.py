from typing import Any

from src.application.contracts.document.document_repository import DocumentRepository
from src.application.prompts.classification import (
    DOCUMENT_CLASSIFICATION_PROMPT_VERSION,
    DocumentClassificationPromptBuilder,
)
from src.application.services.ai import LLMService
from src.application.services.classification import ClassificationService
from src.application.validation.classification import DocumentClassificationValidator
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
from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType, ModelProcessingMetadata
from src.domain.document import Document, DocumentGraph
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator, IdPrefix


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
        prompt_builder: DocumentClassificationPromptBuilder | None = None,
        classification_model: str | None = None,
        document_repository: DocumentRepository | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.classification_service = classification_service
        self.document_classification_validator = document_classification_validator
        self.id_generator = id_generator
        self.document_repository = document_repository
        self.prompt_builder = prompt_builder or DocumentClassificationPromptBuilder()
        self.classification_model = (
            classification_model
            or _default_document_classification_model()
        )
        self.response_parser = ClassificationResponseParser()

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
    ) -> DocumentClassification | None:
        from src.config.settings import classification_settings

        document = self._resolve_document(document_graph)

        if not classification_settings.allow_reclassification:
            existing = self.classification_service.get_document_classification(
                document.document_id
            )
            if existing is not None:
                return existing

        if classification_settings.use_cache:
            cached = self._reuse_cached_classification(
                document, activity_context=activity_context
            )
            if cached is not None:
                return cached

        prompt = self.prompt_builder.build(document_graph)
        response = self.llm_service.generate(
            prompt,
            model=self.classification_model,
            activity_context=activity_context,
            response_schema=build_classification_response_json_schema(),
        )

        classification = self._build_classification(document, response)
        assert classification.result is not None

        if not classification_settings.store_reasoning:
            classification.result.rationale = None
            classification.result.evidence = []

        if not classification.result.is_confident(
            classification_settings.confidence_threshold
        ):
            return None

        validation = self.document_classification_validator.validate(classification)
        validation.raise_if_invalid()

        self.classification_service.save_document_classification(
            classification,
            activity_context=activity_context,
        )
        return classification

    def _reuse_cached_classification(
        self,
        document: Document,
        activity_context: ActivityContext | None = None,
    ) -> DocumentClassification | None:
        if self.document_repository is None:
            return None

        content_hash = document.hashes.content_hash
        if not content_hash:
            return None

        other_document_id = self.document_repository.find_document_id_by_content_hash(
            content_hash
        )
        if other_document_id is None or other_document_id == document.document_id:
            return None

        cached = self.classification_service.get_document_classification(
            other_document_id
        )
        if cached is None or cached.result is None:
            return None

        cached_result = cached.result
        result = ClassificationResult(
            classification_id=self.id_generator.new_id(IdPrefix.CLASSIFICATION),
            document_id=document.document_id,
            predicted_label=cached_result.predicted_label,
            confidence_score=cached_result.confidence_score,
            rationale=cached_result.rationale,
            evidence=list(cached_result.evidence),
        )
        classification = DocumentClassification(
            document_id=document.document_id,
            document_type=cached.document_type,
            result=result,
        )

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
        document_type = resolve_enum_label(parsed.label, DocumentType)
        metadata_errors = build_unknown_label_errors(parsed.label, document_type)

        result = ClassificationResult(
            classification_id=self.id_generator.new_id(IdPrefix.CLASSIFICATION),
            document_id=document.document_id,
            predicted_label=document_type.value,
            confidence_score=parsed.confidence_score,
            rationale=parsed.rationale,
            evidence=parsed.evidence,
            processing_metadata=ModelProcessingMetadata(
                model_name=self.classification_model or "default",
                model_type="document_classification",
                confidence=parsed.confidence_score,
                prompt_version=getattr(
                    self.prompt_builder,
                    "prompt_version",
                    DOCUMENT_CLASSIFICATION_PROMPT_VERSION,
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
    def _resolve_document(document_graph: DocumentGraph | Document) -> Document:
        if isinstance(document_graph, DocumentGraph):
            return document_graph.document
        return document_graph
