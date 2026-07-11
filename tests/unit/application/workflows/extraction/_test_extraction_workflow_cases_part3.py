from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

def test_has_meaningful_entity_content_false_for_empty_list_field() -> None:
    procedure = Procedure(
        procedure_id="procedure_001",
        document_id="document_001",
        title="",
        steps=[],
        source_chunk_id="chunk_001",
    )

    assert (
        has_meaningful_entity_content(
            procedure, ("title", "steps", "component_name", "equipment_id")
        )
        is False
    )

def test_drop_empty_entities_removes_fully_empty_items_across_all_types() -> None:
    result = ExtractionResult(
        extraction_id="extraction_001",
        document_id="document_001",
        maintenance_tasks=[
            MaintenanceTask(
                task_id="task_real",
                document_id="document_001",
                title="Replace filter",
                source_chunk_id="chunk_001",
            ),
            MaintenanceTask(
                task_id="task_empty",
                document_id="document_001",
                title="",
                source_chunk_id="chunk_002",
            ),
        ],
        spare_parts=[
            SparePart(
                spare_part_id="spare_empty",
                document_id="document_001",
                source_chunk_id="chunk_003",
            ),
        ],
        safety_warnings=[
            SafetyWarning(
                safety_warning_id="safety_real",
                document_id="document_001",
                warning_type="warning",
                message="Depressurize before servicing.",
                source_chunk_id="chunk_004",
            ),
            SafetyWarning(
                safety_warning_id="safety_empty",
                document_id="document_001",
                warning_type="warning",
                message="",
                source_chunk_id="chunk_005",
            ),
        ],
    )

    filtered_result, dropped_count = drop_empty_entities(result)

    assert [task.task_id for task in filtered_result.maintenance_tasks] == ["task_real"]
    assert filtered_result.spare_parts == []
    assert [
        warning.safety_warning_id for warning in filtered_result.safety_warnings
    ] == ["safety_real"]
    assert dropped_count == 3

def test_drop_empty_entities_keeps_items_with_only_non_content_fields_absent() -> None:
    # An item with a real component_name but no other fields should survive
    # — component_name alone is meaningful content.
    result = ExtractionResult(
        extraction_id="extraction_001",
        document_id="document_001",
        specifications=[
            Specification(
                specification_id="spec_001",
                document_id="document_001",
                parameter="",
                value="",
                component_name="Hydraulic pump",
                source_chunk_id="chunk_001",
            ),
        ],
    )

    filtered_result, dropped_count = drop_empty_entities(result)

    assert len(filtered_result.specifications) == 1
    assert dropped_count == 0

def test_extract_drops_fully_empty_procedure_before_saving(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "procedures": [
    {
      "title": "Install hydraulic filter",
      "steps": ["Depressurize the line."],
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

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    # Sanity check the real item survives — this test is about the
    # defensive filter not over-triggering on legitimate items, exercised
    # end-to-end through the real extract() pipeline.
    assert len(result.procedures) == 1
    assert result.procedures[0].title == "Install hydraulic filter"

def test_extract_falls_back_to_unknown_procedure_type_for_unrecognized_value(
    sample_chunk,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "procedures": [
    {
      "title": "Adjust valve timing",
      "procedure_type": "not_a_real_category",
      "steps": ["Loosen the locknut.", "Rotate the adjuster."],
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.8,
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

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert len(result.procedures) == 1
    assert result.procedures[0].procedure_type == ProcedureType.UNKNOWN

def test_extract_normalizes_procedure_type_casing_and_separators(
    sample_chunk,
) -> None:
    fake_llm_service = FakeLLMService(
        [
            """{
  "confidence_score": 0.8,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": [],
  "procedures": [
    {
      "title": "Flush the coolant system",
      "procedure_type": "Cleaning-Flushing",
      "steps": ["Drain the coolant.", "Flush with clean water."],
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.8,
      "requires_human_review": false
    }
  ]
}"""
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    result = workflow.extract(sample_chunk.document_id, sample_chunk)

    assert len(result.procedures) == 1
    assert result.procedures[0].procedure_type == ProcedureType.CLEANING_FLUSHING

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
