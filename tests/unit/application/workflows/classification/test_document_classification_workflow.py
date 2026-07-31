import pytest

from src.application.validation.classification import DocumentClassificationValidator
from src.application.workflows.classification import DocumentClassificationWorkflow
from src.application.prompts.classification import (
    DocumentClassificationPromptBuilder,
)
from src.config.settings import classification_settings
from src.domain.classification import ClassificationResult, DocumentClassification
from src.domain.common import DocumentType
from src.shared.exceptions import SchemaValidationError
from src.shared.execution import ActionResult
from src.shared.ids import IdGenerator


class FakeLLMService:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        activity_context=None,
        *,
        response_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "response_schema": response_schema,
            }
        )
        return self.responses.pop(0)


class FakeClassificationService:
    def __init__(self, existing_by_document_id=None) -> None:
        self.saved_document_classifications = []
        self._existing_by_document_id = dict(existing_by_document_id or {})

    def save_document_classification(
        self,
        classification,
        activity_context=None,
    ) -> ActionResult:
        self.saved_document_classifications.append(classification)
        self._existing_by_document_id[classification.document_id] = classification
        return ActionResult(
            entity_type="document",
            entity_id=classification.document_id,
        )

    def get_document_classification(self, document_id):
        return self._existing_by_document_id.get(document_id)


class FakeDocumentRepository:
    def __init__(self, content_hash_matches=None) -> None:
        self.content_hash_matches = dict(content_hash_matches or {})

    def find_document_id_by_content_hash(self, content_hash: str) -> str | None:
        return self.content_hash_matches.get(content_hash)


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
    document_repository: FakeDocumentRepository | None = None,
) -> tuple[DocumentClassificationWorkflow, SpyDocumentClassificationValidator]:
    spy_validator = validator or SpyDocumentClassificationValidator()
    workflow = DocumentClassificationWorkflow(
        llm_service=fake_llm_service,
        classification_service=fake_classification_service,
        document_classification_validator=spy_validator,
        id_generator=IdGenerator(),
        prompt_builder=DocumentClassificationPromptBuilder(),
        classification_model="qwen3:8b",
        document_repository=document_repository,
    )
    return workflow, spy_validator


def test_classify_document_builds_classification_and_saves_it(
    sample_document_graph,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            '{"label": "manual", "confidence_score": 0.91, '
            '"rationale": "The graph summary and content match a maintenance manual.", '
            '"evidence": ["Hydraulic Pump Manual", "Replace hydraulic filter every 1000 operating hours."]}'
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_document(sample_document_graph)

    assert classification is not None
    assert classification.document_id == sample_document_graph.document.document_id
    assert classification.document_type == DocumentType.MANUAL
    assert classification.result is not None
    assert classification.result.classification_id.startswith("classification_")
    assert classification.result.predicted_label == DocumentType.MANUAL.value
    assert classification.result.processing_metadata is not None
    assert classification.result.processing_metadata.model_name == "qwen3:8b"
    assert classification.result.processing_metadata.model_type == "document_classification"
    assert fake_classification_service.saved_document_classifications == [classification]
    assert validator.calls == [classification]
    assert len(fake_llm_service.calls) == 1
    assert fake_llm_service.calls[0]["model"] == "qwen3:8b"
    assert sample_document_graph.document.file_name in fake_llm_service.calls[0]["prompt"]
    assert sample_document_graph.document.title in fake_llm_service.calls[0]["prompt"]
    assert "Replace hydraulic filter every 1000 operating hours." in fake_llm_service.calls[0]["prompt"]
    assert "Spare parts table" in fake_llm_service.calls[0]["prompt"]
    assert isinstance(fake_llm_service.calls[0]["response_schema"], dict)


def test_classify_document_raises_when_validator_rejects_response(
    sample_document_graph,
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
        workflow.classify_document(sample_document_graph)

    assert validator.calls == []
    assert fake_classification_service.saved_document_classifications == []


def test_classify_document_raises_on_malformed_response(sample_document_graph) -> None:
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
        workflow.classify_document(sample_document_graph)

    assert validator.calls == []
    assert fake_classification_service.saved_document_classifications == []


def test_classify_document_still_supports_document_only_input(
    sample_document,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            '{"label": "manual", "confidence_score": 0.81, '
            '"rationale": "The title indicates a manual.", '
            '"evidence": ["Hydraulic Pump Manual"]}'
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_document(sample_document)

    assert classification is not None
    assert classification.document_id == sample_document.document_id
    assert "No graph-derived content summary was available." in fake_llm_service.calls[0]["prompt"]


def test_classify_document_accepts_fenced_json_with_think_block(
    sample_document_graph,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            "<think>I should compare the graph signals first.</think>\n"
            "```json\n"
            "{\n"
            '  "label": "manual",\n'
            '  "confidence_score": 0.87,\n'
            '  "rationale": "The chunk previews and section paths look like a manual.",\n'
            '  "evidence": ["Maintenance Schedule", "Replace hydraulic filter every 1000 operating hours."]\n'
            "}\n"
            "```"
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_document(sample_document_graph)

    assert classification is not None
    assert classification.document_type == DocumentType.MANUAL
    assert classification.result is not None
    assert classification.result.confidence_score == 0.87
    assert fake_classification_service.saved_document_classifications == [classification]
    assert validator.calls == [classification]


def test_classify_document_short_circuits_when_reclassification_is_not_allowed(
    sample_document_graph,
    monkeypatch,
) -> None:
    monkeypatch.setattr(classification_settings, "allow_reclassification", False)
    existing_classification = DocumentClassification(
        document_id=sample_document_graph.document.document_id,
        document_type=DocumentType.MANUAL,
        result=ClassificationResult(
            classification_id="classification_existing",
            document_id=sample_document_graph.document.document_id,
            predicted_label=DocumentType.MANUAL.value,
            confidence_score=0.91,
            rationale="Already classified previously.",
            evidence=["Hydraulic Pump Manual"],
        ),
    )
    fake_llm_service = FakeLLMService([])
    fake_classification_service = FakeClassificationService(
        existing_by_document_id={
            sample_document_graph.document.document_id: existing_classification
        }
    )
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_document(sample_document_graph)

    assert classification is existing_classification
    assert fake_llm_service.calls == []
    assert fake_classification_service.saved_document_classifications == []
    assert validator.calls == []


def test_classify_document_reuses_cached_classification_for_same_content_hash(
    sample_document_graph,
) -> None:
    cached_document_id = "doc_cached"
    cached_classification = DocumentClassification(
        document_id=cached_document_id,
        document_type=DocumentType.MANUAL,
        result=ClassificationResult(
            classification_id="classification_cached",
            document_id=cached_document_id,
            predicted_label=DocumentType.MANUAL.value,
            confidence_score=0.93,
            rationale="Matched an already-classified duplicate document.",
            evidence=["Hydraulic Pump Manual"],
        ),
    )
    fake_llm_service = FakeLLMService([])
    fake_classification_service = FakeClassificationService(
        existing_by_document_id={cached_document_id: cached_classification}
    )
    document_repository = FakeDocumentRepository(
        content_hash_matches={
            sample_document_graph.document.hashes.content_hash: cached_document_id
        }
    )
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
        document_repository=document_repository,
    )

    classification = workflow.classify_document(sample_document_graph)

    assert classification is not None
    assert classification.document_id == sample_document_graph.document.document_id
    assert classification.document_type == DocumentType.MANUAL
    assert classification.result is not None
    assert classification.result.classification_id != "classification_cached"
    assert classification.result.predicted_label == DocumentType.MANUAL.value
    assert classification.result.confidence_score == 0.93
    assert fake_llm_service.calls == []
    assert fake_classification_service.saved_document_classifications == [classification]
    assert validator.calls == []


def test_classify_document_returns_none_when_confidence_is_below_threshold(
    sample_document_graph,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            '{"label": "manual", "confidence_score": 0.10, '
            '"rationale": "Low confidence classification.", '
            '"evidence": []}'
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_document(sample_document_graph)

    assert classification is None
    assert fake_classification_service.saved_document_classifications == []
    assert validator.calls == []


def test_classify_document_clears_reasoning_when_store_reasoning_is_disabled(
    sample_document_graph,
    monkeypatch,
) -> None:
    monkeypatch.setattr(classification_settings, "store_reasoning", False)
    fake_llm_service = FakeLLMService(
        [
            '{"label": "manual", "confidence_score": 0.91, '
            '"rationale": "The graph summary and content match a maintenance manual.", '
            '"evidence": ["Hydraulic Pump Manual"]}'
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_document(sample_document_graph)

    assert classification is not None
    assert classification.result is not None
    assert classification.result.rationale is None
    assert classification.result.evidence == []
    assert fake_classification_service.saved_document_classifications == [classification]
    assert validator.calls == [classification]
