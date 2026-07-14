from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

def test_extract_replaces_existing_result_when_replace_existing_is_true(
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
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(
        sample_chunk.document_id,
        sample_chunk,
        replace_existing=True,
    )

    assert fake_extraction_service.replaced_results == [result]
    assert fake_extraction_service.saved_results == []

def test_hydrate_table_chunks_replaces_partial_content_with_full_table(sample_chunk) -> None:
    table = TableAsset(
        table_id="table_001",
        document_id=sample_chunk.document_id,
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |\n| HP-002 | 2 |",
    )
    partial_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_1",
        content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
        table_ids=["table_001"],
    )

    hydrated = hydrate_table_chunks([partial_chunk], {"table_001": table})

    assert len(hydrated) == 1
    assert "HP-001" in hydrated[0].content
    assert "HP-002" in hydrated[0].content
    assert hydrated[0].chunk_id == "chunk_table_1"

def test_hydrate_table_chunks_drops_later_chunks_sharing_the_same_table(sample_chunk) -> None:
    table = TableAsset(
        table_id="table_001",
        document_id=sample_chunk.document_id,
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |\n| HP-002 | 2 |",
    )
    first_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_1",
        content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
        table_ids=["table_001"],
    )
    second_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_2",
        content="| HP-002 | 2 |",
        table_ids=["table_001"],
    )

    hydrated = hydrate_table_chunks(
        [first_chunk, second_chunk], {"table_001": table}
    )

    assert len(hydrated) == 1
    assert hydrated[0].chunk_id == "chunk_table_1"
    assert "HP-002" in hydrated[0].content

def test_hydrate_table_chunks_leaves_non_table_chunks_unchanged(sample_chunk) -> None:
    hydrated = hydrate_table_chunks([sample_chunk], {})

    assert hydrated == [sample_chunk]

def test_hydrate_table_chunks_appends_structured_row_echo_when_rows_present(
    sample_chunk,
) -> None:
    table = TableAsset(
        table_id="table_001",
        document_id=sample_chunk.document_id,
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |\n| HP-002 | 2 |",
        rows=[["Part", "Qty"], ["HP-001", "1"], ["HP-002", "2"]],
    )
    partial_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_1",
        content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
        table_ids=["table_001"],
    )

    hydrated = hydrate_table_chunks([partial_chunk], {"table_001": table})

    assert "Row 1: Part=HP-001 | Qty=1" in hydrated[0].content
    assert "Row 2: Part=HP-002 | Qty=2" in hydrated[0].content
    # The original markdown text is still present alongside the echo.
    assert "| HP-001 | 1 |" in hydrated[0].content

def test_hydrate_table_chunks_omits_structured_row_echo_when_rows_absent(
    sample_chunk,
) -> None:
    table = TableAsset(
        table_id="table_001",
        document_id=sample_chunk.document_id,
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
    )
    partial_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_1",
        content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
        table_ids=["table_001"],
    )

    hydrated = hydrate_table_chunks([partial_chunk], {"table_001": table})

    assert "Row 1:" not in hydrated[0].content

def test_hydrate_table_chunks_includes_table_caption(sample_chunk) -> None:
    table = TableAsset(
        table_id="table_001",
        document_id=sample_chunk.document_id,
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
    )
    table.metadata.caption = "Spare parts for the hydraulic pump"
    partial_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_1",
        content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
        table_ids=["table_001"],
    )

    hydrated = hydrate_table_chunks([partial_chunk], {"table_001": table})

    assert "Spare parts for the hydraulic pump" in hydrated[0].content


def test_hydrate_table_chunks_includes_structure_context_when_available(
    sample_chunk,
) -> None:
    table = TableAsset(
        table_id="table_001",
        document_id=sample_chunk.document_id,
        markdown="| Parameter | Compact version | Remote version |\n|---|---|---|\n| Pressure range | 0...10 | 0...16 |",
        rows=[
            ["Parameter", "Compact version", "Remote version"],
            ["Pressure range", "0...10", "0...16"],
        ],
        table_shape="specification_matrix",
        header_paths=[
            ["Parameter"],
            ["Field", "Compact version"],
            ["Field", "Remote version"],
        ],
        axis_summary={
            "row_axis": "parameter",
            "column_axis": "field",
            "value_axis": "specification_value",
        },
    )
    partial_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_1",
        content="| Parameter | Compact version | Remote version |\n|---|---|---|\n| Pressure range | 0...10 | 0...16 |",
        table_ids=["table_001"],
    )

    hydrated = hydrate_table_chunks([partial_chunk], {"table_001": table})

    assert "Table shape: specification_matrix" in hydrated[0].content
    assert "Header paths: Parameter | Field > Compact version | Field > Remote version" in hydrated[0].content

def test_extract_hydrates_split_table_chunks_before_building_prompt(sample_chunk) -> None:
    table = TableAsset(
        table_id="table_001",
        document_id=sample_chunk.document_id,
        markdown=(
            "| Part Number | Description | Quantity |\n"
            "|---|---|---|\n"
            "| HP-001 | Hydraulic filter | 1 |\n"
            "| HP-002 | Seal kit | 2 |"
        ),
    )
    first_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_1",
        content="| Part Number | Description | Quantity |\n|---|---|---|\n| HP-001 | Hydraulic filter | 1 |",
        table_ids=["table_001"],
    )
    second_chunk = _make_table_chunk(
        sample_chunk,
        chunk_id="chunk_table_2",
        content="| HP-002 | Seal kit | 2 |",
        table_ids=["table_001"],
    )
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [
    {
      "part_number": "HP-002",
      "description": "Seal kit",
      "quantity": "2",
      "source_chunk_id": "chunk_table_1",
      "confidence_score": 0.9,
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

    result = workflow.extract(
        sample_chunk.document_id,
        [first_chunk, second_chunk],
        tables={"table_001": table},
    )

    # Only one chunk should have been sent to the LLM (the other was dropped
    # as redundant once its table was hydrated into the first chunk), and
    # the prompt must contain BOTH rows even though each chunk only held one.
    assert len(fake_llm_service.calls) == 1
    prompt = fake_llm_service.calls[0]["prompt"]
    assert "HP-001" in prompt
    assert "HP-002" in prompt
    assert "chunk_table_2" not in prompt
    assert len(result.spare_parts) == 1
    assert result.spare_parts[0].part_number == "HP-002"

def test_extraction_still_rejects_non_null_invalid_array_items(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "maintenance_tasks": [],
  "spare_parts": ["not an object"],
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
        allow_partial_batches=False,
    )

    with pytest.raises(SchemaValidationError) as exc_info:
        workflow.extract(sample_chunk.document_id, sample_chunk)

    assert "spare_parts" in exc_info.value.details["parse_error"]
