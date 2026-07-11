from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

def test_extract_populates_source_metadata_with_graph_context(sample_chunk) -> None:
    section_id = sample_chunk.section_id
    chunk_1 = DocumentChunk(
        chunk_id="chunk_001",
        document_id=sample_chunk.document_id,
        section_id=section_id,
        content="First chunk about the hydraulic filter.",
        section_path=sample_chunk.section_path,
        element_ids=["el_001"],
        table_ids=["table_001"],
        source=sample_chunk.source,
        chunk_index=1,
    )
    chunk_2 = DocumentChunk(
        chunk_id="chunk_002",
        document_id=sample_chunk.document_id,
        section_id=section_id,
        content="Middle chunk about the hydraulic filter.",
        section_path=sample_chunk.section_path,
        element_ids=["el_002"],
        source=sample_chunk.source,
        chunk_index=2,
    )
    chunk_3 = DocumentChunk(
        chunk_id="chunk_003",
        document_id=sample_chunk.document_id,
        section_id=section_id,
        content="Third chunk about the hydraulic filter.",
        section_path=sample_chunk.section_path,
        element_ids=["el_003"],
        source=sample_chunk.source,
        chunk_index=3,
    )
    section = DocumentSection(
        section_id=section_id,
        document_id=sample_chunk.document_id,
        title="Maintenance Schedule",
        parent_section_id="section_root",
    )

    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.9,
  "requires_human_review": false,
  "maintenance_tasks": [
    {
      "title": "Replace hydraulic filter",
      "interval": "1000 operating hours",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.9,
      "requires_human_review": false
    },
    {
      "title": "Inspect hydraulic filter",
      "interval": "500 operating hours",
      "source_chunk_id": "chunk_002",
      "confidence_score": 0.9,
      "requires_human_review": false
    },
    {
      "title": "Clean hydraulic filter housing",
      "interval": "250 operating hours",
      "source_chunk_id": "chunk_003",
      "confidence_score": 0.9,
      "requires_human_review": false
    }
  ],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": []
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        enable_candidate_narrowing=False,
    )

    result = workflow.extract(
        sample_chunk.document_id,
        [chunk_1, chunk_2, chunk_3],
        sections={section_id: section},
    )

    tasks_by_chunk = {task.source_chunk_id: task for task in result.maintenance_tasks}

    first_metadata = tasks_by_chunk["chunk_001"].source_metadata
    assert first_metadata.document_id == sample_chunk.document_id
    assert first_metadata.chunk_id == "chunk_001"
    assert first_metadata.section_id == section_id
    assert first_metadata.section_path == tuple(sample_chunk.section_path)
    assert first_metadata.page_start == sample_chunk.source.page_start
    assert first_metadata.page_end == sample_chunk.source.page_end
    assert first_metadata.parent_section_id == "section_root"
    assert first_metadata.table_id == "table_001"
    assert first_metadata.source_element_ids == ("el_001",)
    assert first_metadata.nearby_chunk_ids == ("chunk_002",)

    middle_metadata = tasks_by_chunk["chunk_002"].source_metadata
    assert middle_metadata.table_id is None
    assert middle_metadata.nearby_chunk_ids == ("chunk_001", "chunk_003")

    last_metadata = tasks_by_chunk["chunk_003"].source_metadata
    assert last_metadata.nearby_chunk_ids == ("chunk_002",)

def test_extract_uses_full_prompt_when_narrowing_disabled(sample_chunk) -> None:
    safety_chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content="Danger: disconnect power before servicing.",
        chunk_type=ChunkType.SAFETY_WARNING,
        source=sample_chunk.source,
    )
    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        enable_candidate_narrowing=False,
    )

    workflow.extract(sample_chunk.document_id, [safety_chunk])

    prompt = fake_llm_service.calls[0]["prompt"]
    assert '"procedures": [' in prompt
    assert '"troubleshooting_entries": [' in prompt

def test_extract_narrows_prompt_when_candidate_narrowing_enabled(sample_chunk) -> None:
    safety_chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content="Danger: disconnect power before servicing.",
        chunk_type=ChunkType.SAFETY_WARNING,
        section_path=["Safety"],
        source=sample_chunk.source,
    )
    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        enable_candidate_narrowing=True,
    )

    workflow.extract(sample_chunk.document_id, [safety_chunk])

    prompt = fake_llm_service.calls[0]["prompt"]
    assert '"safety_warnings": [' in prompt
    assert '"identifiers": [' in prompt
    assert '"procedures": [' not in prompt
    assert '"troubleshooting_entries": [' not in prompt
    assert '"spare_parts": [' not in prompt

def test_extract_falls_back_to_full_prompt_when_union_candidates_cover_everything(
    sample_chunk,
) -> None:
    chunk_a = DocumentChunk(
        chunk_id="chunk_001",
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content="Danger: disconnect power before servicing.",
        chunk_type=ChunkType.SAFETY_WARNING,
        source=sample_chunk.source,
        chunk_index=1,
    )
    chunk_b = DocumentChunk(
        chunk_id="chunk_002",
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content="General overview content.",
        chunk_type=ChunkType.GENERAL,
        source=sample_chunk.source,
        chunk_index=2,
    )
    # No LLM candidate-router is wired into make_workflow(), so a GENERAL
    # chunk (chunk_b) already resolves deterministically to "every entity
    # type" (ExtractionCandidateSelector.select_for_chunk() fails open to
    # _ALL_CANDIDATES with no router configured) -- the union covering
    # everything, and the resulting full-prompt fallback, both happen without
    # any narrowing LLM call. Only the actual extraction call happens.
    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        enable_candidate_narrowing=True,
    )

    workflow.extract(sample_chunk.document_id, [chunk_a, chunk_b])

    assert len(fake_llm_service.calls) == 1
    prompt = fake_llm_service.calls[0]["prompt"]
    assert '"procedures": [' in prompt
    assert '"troubleshooting_entries": [' in prompt
    assert '"spare_parts": [' in prompt

def test_extract_emits_narrowed_progress_message_when_narrowing_applied(
    sample_chunk,
) -> None:
    safety_chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content="Danger: disconnect power before servicing.",
        chunk_type=ChunkType.SAFETY_WARNING,
        source=sample_chunk.source,
    )
    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        enable_candidate_narrowing=True,
    )
    progress_messages: list[str] = []

    workflow.extract(
        sample_chunk.document_id,
        [safety_chunk],
        progress_callback=progress_messages.append,
    )

    assert any("Narrowed extraction to:" in message for message in progress_messages)
    assert any("safety_warning" in message for message in progress_messages)

def test_has_meaningful_entity_content_false_when_all_content_fields_empty() -> None:
    task = MaintenanceTask(
        task_id="task_001",
        document_id="document_001",
        title="",
        source_chunk_id="chunk_001",
    )

    assert (
        has_meaningful_entity_content(task, ("title", "description", "interval"))
        is False
    )

def test_has_meaningful_entity_content_true_when_string_field_set() -> None:
    task = MaintenanceTask(
        task_id="task_001",
        document_id="document_001",
        title="Replace filter",
        source_chunk_id="chunk_001",
    )

    assert (
        has_meaningful_entity_content(task, ("title", "description", "interval"))
        is True
    )

def test_has_meaningful_entity_content_true_for_non_string_field() -> None:
    procedure = Procedure(
        procedure_id="procedure_001",
        document_id="document_001",
        title="",
        equipment_id="equipment_001",
        source_chunk_id="chunk_001",
    )

    assert (
        has_meaningful_entity_content(
            procedure, ("title", "steps", "component_name", "equipment_id")
        )
        is True
    )
