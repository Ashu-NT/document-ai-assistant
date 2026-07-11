from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

def test_extraction_isolates_failed_multi_chunk_batch_to_single_chunk_retries(
    sample_chunk,
) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="This chunk will keep failing schema parsing.",
    )
    third_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_003",
        content="Model ZX-300 requires quarterly inspection.",
    )
    fake_llm_service = FakeLLMService(
        [
            "Still not JSON.",
            """{
  "confidence_score": 0.9,
  "identifiers": [{"value": "QP100A", "identifier_type": "model_number"}],
  "spare_parts": [],
  "maintenance_tasks": [],
  "equipment": [],
  "manufacturers": []
}""",
            "Still not JSON.",
            """{
  "confidence_score": 0.92,
  "identifiers": [{"value": "ZX-300", "identifier_type": "model_number"}],
  "spare_parts": [],
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
        max_attempts=1,
        allow_partial_batches=True,
        chunk_batcher=ExtractionChunkBatcher(
            max_chunks_per_batch=6,
            max_chars_per_batch=50_000,
        ),
    )
    progress_messages: list[str] = []

    result = workflow.extract(
        sample_chunk.document_id,
        [sample_chunk, second_chunk, third_chunk],
        progress_callback=progress_messages.append,
    )

    assert [identifier.raw_value for identifier in result.extracted_identifiers] == [
        "QP100A",
        "ZX-300",
    ]
    assert result.source_chunk_ids == ["chunk_001", "chunk_003"]
    assert result.attempted_chunk_ids == ["chunk_001", "chunk_002", "chunk_003"]
    assert result.unresolved_chunk_ids == ["chunk_002"]
    assert any(
        "Persistently failing batch contains 3 chunk(s)." in message
        for message in progress_messages
    )
    assert any(
        "Isolating chunk 2/3: chunk_002" in message for message in progress_messages
    )

def test_extraction_allows_overriding_temperature_and_json_mode(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        temperature=0.4,
        json_mode=False,
    )

    workflow.extract(sample_chunk.document_id, sample_chunk)

    assert fake_llm_service.calls[0]["temperature"] == 0.4
    assert fake_llm_service.calls[0]["json_mode"] is False
    assert isinstance(fake_llm_service.calls[0]["response_schema"], dict)

def test_extraction_passes_json_schema_for_constrained_decoding_when_json_mode_enabled(
    sample_chunk,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        json_mode=True,
    )

    workflow.extract(sample_chunk.document_id, sample_chunk)

    schema = fake_llm_service.calls[0]["response_schema"]
    assert isinstance(schema, dict)
    assert schema["properties"]["identifiers"]["items"]["$ref"] == "#/$defs/IdentifierPayload"

def test_extraction_repairs_truncated_json_response(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "maintenance_tasks": [],
  "spare_parts": [
    {"part_number": "FLT-100", "description": "Filter Element"},
  ],
  "equipment": [],
  "manufacturers": [],
  "identifiers": [
"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        allow_partial_batches=False,
    )

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.confidence_score == pytest.approx(0.8)
    assert len(result.spare_parts) == 1
    assert result.spare_parts[0].part_number == "FLT-100"
    assert result.extracted_identifiers == []

def test_extraction_rejects_truncated_json_response_when_cut_mid_string(
    sample_chunk,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "maintenance_tasks": [],
  "spare_parts": [
    {"part_number": "FLT-100", "description": "Filter"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        allow_partial_batches=False,
    )

    with pytest.raises(SchemaValidationError):
        workflow.extract(sample_chunk.document_id, sample_chunk)

def test_extraction_drops_json_artifact_placeholder_values(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.84,
  "maintenance_intervals": [
    {"interval": ":[{"},
    {"interval": "]"},
    {"interval": "Every 500 hours", "source_chunk_id": "chunk_001"}
  ],
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert len(result.maintenance_intervals) == 1
    assert result.maintenance_intervals[0].interval == "Every 500 hours"

def test_extraction_rejects_null_array_items(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "requires_human_review": false,
  "maintenance_tasks": [
    {
      "title": "Ensure system modifications are approved",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.9,
      "requires_human_review": false
    }
  ],
  "spare_parts": [null],
  "equipment": [null],
  "manufacturers": [null],
  "identifiers": [
    {
      "raw_value": "FWC12",
      "identifier_type": "model_number",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.9,
      "requires_human_review": false
    }
  ]
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        allow_partial_batches=False,
    )
    with pytest.raises(SchemaValidationError):
        workflow.extract(sample_chunk.document_id, sample_chunk)

def test_extraction_rejects_mixed_null_and_valid_array_items(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "maintenance_tasks": [],
  "spare_parts": [null, {"part_number": "FLT-100", "description": "Filter Element"}],
  "equipment": [],
  "manufacturers": [],
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    with pytest.raises(SchemaValidationError):
        workflow.extract(sample_chunk.document_id, sample_chunk)
