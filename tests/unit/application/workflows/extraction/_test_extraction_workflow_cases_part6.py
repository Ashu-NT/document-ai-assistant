from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

def test_extraction_gives_up_on_batch_after_exhausting_retries(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "Not JSON, attempt one.",
            "Not JSON, attempt two.",
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        max_attempts=2,
        allow_partial_batches=False,
    )

    with pytest.raises(SchemaValidationError) as exc_info:
        workflow.extract(sample_chunk.document_id, sample_chunk)

    assert len(fake_llm_service.calls) == 2
    assert exc_info.value.details["batch_index"] == 1
    assert exc_info.value.details["batch_count"] == 1

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
        allow_partial_batches=False,
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
        allow_partial_batches=False,
    )

    with pytest.raises(SchemaValidationError) as exc_info:
        workflow.extract(sample_chunk.document_id, [sample_chunk, second_chunk])

    assert exc_info.value.details["batch_index"] == 2
    assert exc_info.value.details["batch_count"] == 2
    assert exc_info.value.details["chunk_ids"] == ["chunk_002"]
    assert "[path]" in exc_info.value.details["raw_response_preview"]
    assert "C:\\Users\\ashuf\\secret\\device.pdf" not in exc_info.value.details["raw_response_preview"]
    assert fake_extraction_service.saved_results == []

def test_extraction_emits_failure_preview_progress_message(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [
    null
  ],
  "identifiers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        allow_partial_batches=False,
    )
    progress_messages: list[str] = []

    with pytest.raises(SchemaValidationError):
        workflow.extract(
            sample_chunk.document_id,
            sample_chunk,
            progress_callback=progress_messages.append,
        )

    assert any(
        "Schema parsing failed:" in message and "Response preview:" in message
        for message in progress_messages
    )

def test_extraction_flags_invalid_source_chunk_id_for_human_review_instead_of_failing(
    sample_chunk,
) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="Filter element FLT-100 is used in QP100A.",
    )
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "maintenance_tasks": [],
  "spare_parts": [
    {
      "part_number": "FLT-100",
      "description": "Filter Element",
      "source_chunk_id": "chunk_999_does_not_exist"
    }
  ],
  "equipment": [],
  "manufacturers": [],
  "identifiers": [
    {
      "raw_value": "QP100A",
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
    progress_messages: list[str] = []

    result = workflow.extract(
        sample_chunk.document_id,
        [sample_chunk, second_chunk],
        progress_callback=progress_messages.append,
    )

    assert len(result.spare_parts) == 1
    assert result.spare_parts[0].part_number == "FLT-100"
    assert result.spare_parts[0].source_chunk_id is None
    assert result.spare_parts[0].requires_human_review is True
    assert len(result.extracted_identifiers) == 1
    assert result.extracted_identifiers[0].source_chunk_id == "chunk_001"
    assert result.extracted_identifiers[0].requires_human_review is False
    assert any(
        "item(s) referenced a source_chunk_id outside this batch" in message
        for message in progress_messages
    )

def test_extraction_skips_persistently_failing_batch_when_partial_batches_allowed(
    sample_chunk,
) -> None:
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
            "Still not JSON.",
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        max_attempts=1,
        allow_partial_batches=True,
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

    assert len(result.extracted_identifiers) == 1
    assert result.requires_human_review is True
    assert result.unresolved_chunk_ids == ["chunk_002"]
    assert any(
        "Extraction completed with unresolved chunk(s) pending retry: ['chunk_002']."
        in message
        for message in progress_messages
    )
