import pytest

from src.application.prompts.extraction import IdentifierExtractionPromptBuilder
from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.extraction.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
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
    **kwargs,
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
        **kwargs,
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
    assert result.maintenance_tasks[0].source.page_start == sample_chunk.source.page_start
    assert result.spare_parts[0].source.page_start == second_chunk.source.page_start
    assert fake_extraction_service.saved_results == [result]
    assert validator.calls == [result]
    assert sample_chunk.content in fake_llm_service.calls[0]["prompt"]
    assert second_chunk.content in fake_llm_service.calls[0]["prompt"]
    assert fake_llm_service.calls[0]["model"] == "qwen3:8b"


def test_extract_parses_identifiers_from_llm_response(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.85,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": [
    {
      "raw_value": "DRG-5001",
      "identifier_type": "drawing_number",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.9,
      "requires_human_review": false
    },
    {
      "raw_value": "ISO 9001",
      "identifier_type": "certificate_number",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.95,
      "requires_human_review": false
    }
  ]
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert len(result.extracted_identifiers) == 2
    drawing = result.extracted_identifiers[0]
    assert drawing.raw_value == "DRG-5001"
    assert drawing.identifier_type == "drawing_number"
    assert drawing.source_chunk_id == sample_chunk.chunk_id
    cert = result.extracted_identifiers[1]
    assert cert.raw_value == "ISO 9001"
    assert cert.identifier_type == "certificate_number"


def test_extract_identifiers_omitted_returns_empty_list(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.7,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.extracted_identifiers == []


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


def test_extract_parses_think_block_and_fenced_json(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """<think>I should inspect the chunk carefully before returning JSON.</think>

```json
{
  "overall_confidence": "91%",
  "requires_review": false,
  "tasks": [
    {
      "title": "Inspect oil level",
      "interval": "Daily",
      "source_chunk_id": "chunk_001",
      "confidence": "0.9",
      "requires_review": false
    }
  ],
  "parts": [],
  "equipment_info": [],
  "manufacturer_list": [],
  "identifier_list": []
}
```"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.confidence_score == pytest.approx(0.91)
    assert result.requires_human_review is False
    assert len(result.maintenance_tasks) == 1
    assert result.maintenance_tasks[0].title == "Inspect oil level"
    assert result.maintenance_tasks[0].interval == "Daily"


def test_extract_emits_progress_messages(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)
    progress_messages: list[str] = []

    workflow.extract(
        sample_chunk.document_id,
        sample_chunk,
        progress_callback=progress_messages.append,
    )

    assert any(
        "Preparing extraction input from 1 final chunk(s)" in message
        for message in progress_messages
    )
    assert any(
        "Prepared 1 extraction batch(es)." in message
        for message in progress_messages
    )
    assert any(
        "[extraction 1/1] Building extraction prompt from 1 chunk(s)" in message
        for message in progress_messages
    )
    assert any(
        "[extraction 1/1] Calling extraction model qwen3:8b" in message
        for message in progress_messages
    )
    assert any(
        "Extraction model response received. Parsing structured payload" in message
        for message in progress_messages
    )
    assert any(
        "Validating extraction result" in message
        for message in progress_messages
    )
    assert any(
        "Saving extraction result" in message
        for message in progress_messages
    )
    assert any(
        "Extraction completed (maintenance_tasks=0, spare_parts=0, equipment=0, manufacturers=0, identifiers=0, batches=1)." in message
        for message in progress_messages
    )


def test_extract_parses_yaml_style_response(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """confidence_score: 0.86
requires_human_review: false
maintenance_tasks:
  - title: Inspect terminal wiring
    description: Verify the terminal wiring and tighten if necessary.
    interval: During commissioning
    source_chunk_id: chunk_001
    confidence_score: 0.84
    requires_human_review: false
spare_parts: []
equipment:
  - name: Pressure transmitter
    model_number: PT-500
    serial_number: SN-7788
    source_chunk_id: chunk_001
    confidence_score: 0.87
    requires_human_review: false
manufacturers: []
identifiers:
  - raw_value: PT-500
    identifier_type: model_number
    source_chunk_id: chunk_001
    confidence_score: 0.9
    requires_human_review: false
"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.confidence_score == pytest.approx(0.86)
    assert len(result.maintenance_tasks) == 1
    assert result.maintenance_tasks[0].title == "Inspect terminal wiring"
    assert len(result.equipment) == 1
    assert result.equipment[0].model_number == "PT-500"
    assert len(result.extracted_identifiers) == 1
    assert result.extracted_identifiers[0].raw_value == "PT-500"


def test_extraction_batches_large_chunk_set_by_char_limit(sample_chunk) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="Valve inspection checklist " * 8,
    )
    third_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_003",
        content="Filter maintenance schedule " * 8,
    )
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}""",
            """{
  "confidence_score": 0.82,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}""",
            """{
  "confidence_score": 0.84,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}""",
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        chunk_batcher=ExtractionChunkBatcher(
            max_chunks_per_batch=10,
            max_chars_per_batch=280,
        ),
    )

    workflow.extract(
        sample_chunk.document_id,
        [sample_chunk, second_chunk, third_chunk],
    )

    assert len(fake_llm_service.calls) == 2
    assert all("Chunk id:" in call["prompt"] for call in fake_llm_service.calls)


def test_extraction_small_document_uses_single_batch(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    workflow.extract(sample_chunk.document_id, sample_chunk)

    assert len(fake_llm_service.calls) == 1
    assert workflow.last_batch_diagnostics[0].batch_count == 1


def test_extraction_merges_partial_results_and_deduplicates_identifiers(sample_chunk) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="Filter element FLT-100 is used in QP100A.",
    )
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "identifiers": [{"value": "QP100A", "identifier_type": "model_number"}],
  "spare_parts": [],
  "maintenance_tasks": [],
  "equipment": [],
  "manufacturers": []
}""",
            """{
  "confidence_score": 0.85,
  "identifiers": [{"value": "QP100A", "identifier_type": "model_number"}],
  "spare_parts": [{"part_number": "FLT-100", "description": "Filter Element"}],
  "maintenance_tasks": [],
  "equipment": [],
  "manufacturers": []
}""",
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        chunk_batcher=ExtractionChunkBatcher(
            max_chunks_per_batch=1,
            max_chars_per_batch=10_000,
        ),
    )

    result = workflow.extract(sample_chunk.document_id, [sample_chunk, second_chunk])

    assert len(fake_llm_service.calls) == 2
    assert len(result.extracted_identifiers) == 1
    assert result.extracted_identifiers[0].raw_value == "QP100A"
    assert len(result.spare_parts) == 1
    assert result.spare_parts[0].part_number == "FLT-100"
    assert result.confidence_score == pytest.approx((0.9 + 0.85) / 2)


def test_extraction_fails_with_clear_batch_error_and_safe_preview(sample_chunk) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="Chunk that will trigger malformed response.",
    )
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}""",
            "Not JSON. See C:\\Users\\ashuf\\secret\\device.pdf for more details.",
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        chunk_batcher=ExtractionChunkBatcher(
            max_chunks_per_batch=1,
            max_chars_per_batch=10_000,
        ),
    )

    with pytest.raises(SchemaValidationError) as exc_info:
        workflow.extract(sample_chunk.document_id, [sample_chunk, second_chunk])

    assert exc_info.value.details["batch_index"] == 2
    assert exc_info.value.details["batch_count"] == 2
    assert exc_info.value.details["chunk_ids"] == ["chunk_002"]
    assert "[path]" in exc_info.value.details["raw_response_preview"]
    assert "C:\\Users\\ashuf\\secret\\device.pdf" not in exc_info.value.details["raw_response_preview"]
    assert fake_extraction_service.saved_results == []
