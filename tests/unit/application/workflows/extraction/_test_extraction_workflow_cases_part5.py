from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

def test_extraction_ignores_fully_empty_placeholder_items(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.81,
  "requires_human_review": false,
  "maintenance_tasks": [
    {
      "title": "",
      "description": "N/A",
      "interval": null,
      "component_name": "-",
      "equipment_id": null
    }
  ],
  "spare_parts": [
    {
      "part_number": null,
      "description": "N/A",
      "quantity": "",
      "component_name": "not available",
      "manufacturer_name": "-"
    }
  ],
  "equipment": [
    {
      "name": null,
      "model_number": "",
      "serial_number": "N/A",
      "manufacturer_name": "-"
    }
  ],
  "manufacturers": [
    {
      "name": "",
      "website": "N/A",
      "country": null
    }
  ],
  "identifiers": [
    {
      "raw_value": "",
      "identifier_type": "",
      "source_chunk_id": null
    }
  ]
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.maintenance_tasks == []
    assert result.spare_parts == []
    assert result.equipment == []
    assert result.manufacturers == []
    assert result.extracted_identifiers == []

def test_extraction_drops_partial_items_missing_required_fields(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.81,
  "requires_human_review": false,
  "manufacturers": [
    {
      "website": "https://example.com"
    }
  ],
  "specifications": [
    {
      "parameter": "Pressure rating",
      "unit": "bar"
    },
    {
      "value": "16",
      "unit": "bar"
    }
  ],
  "identifiers": [
    {
      "identifier_type": "model_number"
    }
  ]
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        enable_candidate_narrowing=False,
    )

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert result.manufacturers == []
    assert result.specifications == []
    assert result.extracted_identifiers == []

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

def test_extraction_retries_only_the_failed_batch(sample_chunk) -> None:
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
            "Sorry, here is a summary instead of JSON as requested.",
            """{
  "confidence_score": 0.84,
  "identifiers": [],
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
        max_attempts=2,
        chunk_batcher=ExtractionChunkBatcher(
            max_chunks_per_batch=1,
            max_chars_per_batch=10_000,
        ),
    )
    progress_messages: list[str] = []

    result = workflow.extract(
        sample_chunk.document_id,
        [sample_chunk, second_chunk],
        progress_callback=progress_messages.append,
    )

    assert len(fake_llm_service.calls) == 3
    assert len(result.extracted_identifiers) == 1
    assert result.extracted_identifiers[0].raw_value == "QP100A"
    assert len(result.spare_parts) == 1
    assert result.spare_parts[0].part_number == "FLT-100"
    assert any(
        "[extraction 2/2] attempt 1/2 failed schema parsing:" in message
        and "Retrying this batch only" in message
        for message in progress_messages
    )
    assert not any("Restarting extraction from the first batch" in message for message in progress_messages)

def test_extraction_retry_feeds_previous_error_back_into_the_prompt(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "Not JSON at all.",
            """{
  "confidence_score": 0.9,
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
        max_attempts=2,
        allow_partial_batches=False,
    )

    workflow.extract(sample_chunk.document_id, sample_chunk)

    assert len(fake_llm_service.calls) == 2
    assert "Your previous response was rejected" not in fake_llm_service.calls[0]["prompt"]
    assert "Your previous response was rejected" in fake_llm_service.calls[1]["prompt"]
    assert "Malformed extraction response" in fake_llm_service.calls[1]["prompt"]
