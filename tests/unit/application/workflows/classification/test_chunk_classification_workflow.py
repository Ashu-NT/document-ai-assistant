from src.application.validation.classification import ChunkClassificationValidator
from src.application.prompts.classification import ChunkTypePromptBuilder
from src.application.workflows.classification import ChunkClassificationWorkflow
from src.domain.common import ChunkType
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
        self.saved_chunk_classifications = []

    def save_chunk_classification(
        self,
        classification,
        activity_context=None,
    ) -> ActionResult:
        self.saved_chunk_classifications.append(classification)
        return ActionResult(
            entity_type="chunk",
            entity_id=classification.chunk_id,
        )


class SpyChunkClassificationValidator:
    def __init__(self) -> None:
        self.calls = []
        self.delegate = ChunkClassificationValidator()

    def validate(self, value):
        self.calls.append(value)
        return self.delegate.validate(value)


def make_workflow(
    fake_llm_service: FakeLLMService,
    fake_classification_service: FakeClassificationService,
    validator: SpyChunkClassificationValidator | None = None,
) -> tuple[ChunkClassificationWorkflow, SpyChunkClassificationValidator]:
    spy_validator = validator or SpyChunkClassificationValidator()
    workflow = ChunkClassificationWorkflow(
        llm_service=fake_llm_service,
        classification_service=fake_classification_service,
        chunk_classification_validator=spy_validator,
        id_generator=IdGenerator(),
        prompt_builder=ChunkTypePromptBuilder(),
        classification_model="qwen3:8b",
    )
    return workflow, spy_validator


def test_classify_chunk_builds_classification_and_saves_it(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            '{"label": "maintenance_interval", "confidence_score": 0.84, '
            '"rationale": "The chunk describes a recurring maintenance interval.", '
            '"evidence": ["every 1000 operating hours"]}'
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_chunk(sample_chunk)

    assert classification.chunk_id == sample_chunk.chunk_id
    assert classification.document_id == sample_chunk.document_id
    assert classification.chunk_type == ChunkType.MAINTENANCE_INTERVAL
    assert classification.result is not None
    assert classification.result.classification_id.startswith("classification_")
    assert classification.result.predicted_label == ChunkType.MAINTENANCE_INTERVAL.value
    assert classification.result.processing_metadata is not None
    assert classification.result.processing_metadata.model_name == "qwen3:8b"
    assert classification.result.processing_metadata.model_type == "chunk_classification"
    assert fake_classification_service.saved_chunk_classifications == [classification]
    assert validator.calls == [classification]
    assert sample_chunk.content in fake_llm_service.calls[0]["prompt"]
    assert "Maintenance Schedule" in fake_llm_service.calls[0]["prompt"]
    assert fake_llm_service.calls[0]["model"] == "qwen3:8b"


def test_classify_chunk_maps_invalid_label_to_unknown(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "label: made-up-classification\n"
            "confidence_score: 0.35\n"
            "rationale: The content does not fit a supported label.\n"
            "evidence:\n"
            "- Replace hydraulic filter every 1000 operating hours."
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_chunk(sample_chunk)

    assert classification.chunk_type == ChunkType.UNKNOWN
    assert classification.result is not None
    assert classification.result.predicted_label == ChunkType.UNKNOWN.value
    assert classification.result.processing_metadata is not None
    assert classification.result.processing_metadata.errors == [
        "Unknown label returned by model: made-up-classification"
    ]
    assert fake_classification_service.saved_chunk_classifications == [classification]
    assert validator.calls == [classification]


def test_classify_chunk_accepts_fenced_json_with_think_block(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "<think>This looks like a recurring interval classification.</think>\n"
            "```json\n"
            "{\n"
            '  "chunk_type": "maintenance_interval",\n'
            '  "confidence": "84%",\n'
            '  "rationale": "The chunk describes periodic replacement.",\n'
            '  "evidence": ["every 1000 operating hours"]\n'
            "}\n"
            "```"
        ]
    )
    fake_classification_service = FakeClassificationService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_classification_service,
    )

    classification = workflow.classify_chunk(sample_chunk)

    assert classification.chunk_type == ChunkType.MAINTENANCE_INTERVAL
    assert classification.result is not None
    assert classification.result.confidence_score == 0.84
    assert fake_classification_service.saved_chunk_classifications == [classification]
    assert validator.calls == [classification]
