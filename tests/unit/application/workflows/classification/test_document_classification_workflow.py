import pytest

from src.application.validation.classification import DocumentClassificationValidator
from src.application.workflows.classification import DocumentClassificationWorkflow
from src.application.workflows.classification.prompt_builders import (
    ClassificationPromptBuilder,
)
from src.domain.common import DocumentType
from src.shared.exceptions import SchemaValidationError
from src.shared.execution import ActionResult
from src.shared.ids import IdGenerator


class FakeLLMService:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, str | None]] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        activity_context=None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
            }
        )
        return self.responses.pop(0)


class FakeClassificationService:
    def __init__(self) -> None:
        self.saved_document_classifications = []

    def save_document_classification(
        self,
        classification,
        activity_context=None,
    ) -> ActionResult:
        self.saved_document_classifications.append(classification)
        return ActionResult(
            entity_type="document",
            entity_id=classification.document_id,
        )


class SpyDocumentClassificationValidator:
    def __init__(self) -> None:
        self.calls = []
        self.delegate = DocumentClassificationValidator()

    def validate(self, value):
        self.calls.append(value)
        return self.delegate.validate(value)


def make_workflow(
    fake_llm_service: FakeLLMService,
    fake_classification_service: FakeClassificationService,
    validator: SpyDocumentClassificationValidator | None = None,
) -> tuple[DocumentClassificationWorkflow, SpyDocumentClassificationValidator]:
    spy_validator = validator or SpyDocumentClassificationValidator()
    workflow = DocumentClassificationWorkflow(
        llm_service=fake_llm_service,
        classification_service=fake_classification_service,
        document_classification_validator=spy_validator,
        id_generator=IdGenerator(),
        prompt_builder=ClassificationPromptBuilder(),
        classification_model="qwen3:8b",
    )
    return workflow, spy_validator


def test_classify_document_builds_classification_and_saves_it(
    sample_document,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            '{"label": "manual", "confidence_score": 0.91, '
            '"rationale": "The file metadata describes a maintenance manual.", '
            '"evidence": ["pump_manual.pdf", "Hydraulic Pump Manual"]}'
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_document(sample_document)

    assert classification.document_id == sample_document.document_id
    assert classification.document_type == DocumentType.MANUAL
    assert classification.result is not None
    assert classification.result.classification_id.startswith("classification_")
    assert classification.result.predicted_label == DocumentType.MANUAL.value
    assert classification.result.processing_metadata is not None
    assert classification.result.processing_metadata.model_name == "qwen3:8b"
    assert classification.result.processing_metadata.model_type == "document_classification"
    assert fake_classification_service.saved_document_classifications == [classification]
    assert validator.calls == [classification]
    assert fake_llm_service.calls == [
        {
            "prompt": fake_llm_service.calls[0]["prompt"],
            "model": "qwen3:8b",
        }
    ]
    assert sample_document.file_name in fake_llm_service.calls[0]["prompt"]
    assert sample_document.title in fake_llm_service.calls[0]["prompt"]


def test_classify_document_raises_when_validator_rejects_response(
    sample_document,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            '{"label": "manual", "confidence_score": 1.2, '
            '"rationale": "Invalid confidence score.", '
            '"evidence": ["pump_manual.pdf"]}'
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    with pytest.raises(SchemaValidationError):
        workflow.classify_document(sample_document)

    assert len(validator.calls) == 1
    assert fake_classification_service.saved_document_classifications == []


def test_classify_document_raises_on_malformed_response(sample_document) -> None:
    fake_llm_service = FakeLLMService(
        [
            "This answer is not structured in any supported format."
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    with pytest.raises(SchemaValidationError):
        workflow.classify_document(sample_document)

    assert validator.calls == []
    assert fake_classification_service.saved_document_classifications == []
