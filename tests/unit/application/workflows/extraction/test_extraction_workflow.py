import pytest

from src.application.prompts.extraction import IdentifierExtractionPromptBuilder
from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.extraction import ExtractionWorkflow
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


class FakeExtractionService:
    def __init__(self) -> None:
        self.saved_results = []

    def save_extraction_result(
        self,
        result,
        activity_context=None,
    ) -> ActionResult:
        self.saved_results.append(result)
        return ActionResult(
            entity_type="document",
            entity_id=result.document_id,
        )


class SpyExtractionResultValidator:
    def __init__(self) -> None:
        self.calls = []
        self.delegate = ExtractionResultValidator()

    def validate(self, value):
        self.calls.append(value)
        return self.delegate.validate(value)


def clone_chunk(sample_chunk, *, chunk_id: str, content: str):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=sample_chunk.chunk_type,
        section_path=sample_chunk.section_path,
        element_ids=sample_chunk.element_ids,
        table_ids=sample_chunk.table_ids,
        picture_ids=sample_chunk.picture_ids,
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )


def make_workflow(
    fake_llm_service: FakeLLMService,
    fake_extraction_service: FakeExtractionService,
    validator: SpyExtractionResultValidator | None = None,
) -> tuple[ExtractionWorkflow, SpyExtractionResultValidator]:
    spy_validator = validator or SpyExtractionResultValidator()
    workflow = ExtractionWorkflow(
        llm_service=fake_llm_service,
        extraction_service=fake_extraction_service,
        extraction_result_validator=spy_validator,
        id_generator=IdGenerator(),
        prompt_builder=IdentifierExtractionPromptBuilder(),
        extraction_model="qwen3:8b",
        confidence_threshold=0.8,
        require_human_review_default=False,
    )
    return workflow, spy_validator


def test_extract_builds_extraction_result_and_saves_it(sample_chunk) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="Spare part HP-001 is supplied by Example Manufacturer.",
    )
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.91,
  "requires_human_review": false,
  "maintenance_tasks": [
    {
      "title": "Replace hydraulic filter",
      "description": "Replace the hydraulic filter during scheduled maintenance.",
      "interval": "1000 operating hours",
      "component_name": "Hydraulic filter",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.92,
      "requires_human_review": false
    }
  ],
  "spare_parts": [
    {
      "part_number": "HP-001",
      "description": "Hydraulic filter",
      "quantity": "1",
      "manufacturer_name": "Example Manufacturer",
      "source_chunk_id": "chunk_002",
      "confidence_score": 0.88,
      "requires_human_review": false
    }
  ],
  "equipment": [
    {
      "name": "Hydraulic Pump",
      "model_number": "HP-500",
      "manufacturer_name": "Example Manufacturer",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.9,
      "requires_human_review": false
    }
  ],
  "manufacturers": [
    {
      "name": "Example Manufacturer",
      "website": "https://example.com",
      "country": "Germany",
      "source_chunk_id": "chunk_002",
      "confidence_score": 0.87,
      "requires_human_review": false
    }
  ]
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_extraction_service,
    )

    result = workflow.extract(
        sample_chunk.document_id,
        [sample_chunk, second_chunk],
    )

    assert result.document_id == sample_chunk.document_id
    assert result.extraction_id.startswith("extraction_")
    assert result.source_chunk_ids == [sample_chunk.chunk_id, second_chunk.chunk_id]
    assert result.confidence_score == 0.91
    assert result.requires_human_review is False
    assert len(result.maintenance_tasks) == 1
    assert result.maintenance_tasks[0].task_id.startswith("task_")
    assert result.maintenance_tasks[0].source_chunk_id == sample_chunk.chunk_id
    assert len(result.spare_parts) == 1
    assert result.spare_parts[0].spare_part_id.startswith("spare_")
    assert result.spare_parts[0].source_chunk_id == second_chunk.chunk_id
    assert len(result.equipment) == 1
    assert result.equipment[0].equipment_id.startswith("equipment_")
    assert len(result.manufacturers) == 1
    assert result.manufacturers[0].manufacturer_id.startswith("manufacturer_")
    assert fake_extraction_service.saved_results == [result]
    assert validator.calls == [result]
    assert sample_chunk.content in fake_llm_service.calls[0]["prompt"]
    assert second_chunk.content in fake_llm_service.calls[0]["prompt"]
    assert fake_llm_service.calls[0]["model"] == "qwen3:8b"


def test_extract_raises_for_malformed_response(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "This response is not valid extraction JSON."
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, validator = make_workflow(
        fake_llm_service,
        fake_extraction_service,
    )

    with pytest.raises(SchemaValidationError):
        workflow.extract(
            sample_chunk.document_id,
            sample_chunk,
        )

    assert validator.calls == []
    assert fake_extraction_service.saved_results == []
