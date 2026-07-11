from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

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

def test_extract_normalizes_numeric_percentage_top_level_confidence(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 96.37,
  "requires_human_review": false,
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.confidence_score == pytest.approx(0.9637)
    assert result.requires_human_review is False

def test_extract_normalizes_numeric_percentage_item_confidence(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": null,
  "identifiers": [
    {
      "raw_value": "HAM2423501",
      "identifier_type": "serial_number",
      "confidence_score": 87.5
    }
  ]
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.confidence_score == pytest.approx(0.875)
    assert len(result.extracted_identifiers) == 1
    assert result.extracted_identifiers[0].confidence_score == pytest.approx(0.875)

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
        "Extraction completed (maintenance_tasks=0, spare_parts=0, equipment=0, manufacturers=0, suppliers=0, contact_points=0, procedures=0, specifications=0, safety_warnings=0, maintenance_intervals=0, troubleshooting_entries=0, identifiers=0, batches=1)." in message
        for message in progress_messages
    )

def test_extract_rejects_non_json_structured_response(sample_chunk) -> None:
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

    with pytest.raises(SchemaValidationError):
        workflow.extract(sample_chunk.document_id, sample_chunk)

def test_extract_derives_overall_confidence_from_item_confidences(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": null,
  "requires_human_review": null,
  "maintenance_tasks": [],
  "spare_parts": [
    {
      "part_number": "EC881-5",
      "quantity": "2 pcs.",
      "manufacturer_name": "Schauenburg Industrietechnik GmbH",
      "source_chunk_id": "chunk_001",
      "confidence_score": 1.0,
      "requires_human_review": false
    }
  ],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.confidence_score == pytest.approx(1.0)
    assert len(result.spare_parts) == 1
    assert result.spare_parts[0].part_number == "EC881-5"
    assert result.requires_human_review is False

def test_extract_falls_back_to_low_confidence_when_top_level_confidence_missing(
    sample_chunk,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "identifiers": [
    {
      "raw_value": "HAM2423501",
      "identifier_type": "serial_number"
    }
  ]
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.confidence_score == pytest.approx(0.0)
    assert result.requires_human_review is True
    assert len(result.extracted_identifiers) == 1
    assert result.extracted_identifiers[0].raw_value == "HAM2423501"
    assert result.extracted_identifiers[0].confidence_score == pytest.approx(0.0)
