from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

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
  ],
  "suppliers": [
    {
      "name": "FMD Rotterdam",
      "website": "https://fmd-rotterdam.example",
      "country": "Netherlands",
      "source_chunk_id": "chunk_002",
      "confidence_score": 0.86,
      "requires_human_review": false
    }
  ],
  "contact_points": [
    {
      "contact_type": "email_address",
      "value": "service@example.com",
      "label": "service",
      "owner_name": "Example Manufacturer",
      "owner_entity_type": "manufacturer",
      "source_chunk_id": "chunk_002",
      "confidence_score": 0.89,
      "requires_human_review": false
    }
  ],
  "procedures": [
    {
      "title": "Install hydraulic filter",
      "procedure_type": "installation",
      "steps": ["Depressurize the line.", "Remove the old filter.", "Install the new filter."],
      "component_name": "Hydraulic filter",
      "equipment_reference": "Hydraulic Pump",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.89,
      "requires_human_review": false
    }
  ],
  "specifications": [
    {
      "parameter": "Pressure rating",
      "value": "16",
      "unit": "bar",
      "component_name": "Hydraulic pump",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.91,
      "requires_human_review": false
    }
  ],
  "safety_warnings": [
    {
      "warning_type": "danger",
      "message": "Depressurize the hydraulic line before removing the filter housing.",
      "component_name": "Hydraulic filter",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.93,
      "requires_human_review": false
    }
  ],
  "maintenance_intervals": [
    {
      "component_name": "Hydraulic filter",
      "interval": "1000 operating hours",
      "task_reference": "Replace hydraulic filter",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.9,
      "requires_human_review": false
    }
  ],
  "troubleshooting_entries": [
    {
      "symptom": "Pump fails to build pressure",
      "cause": "Worn hydraulic filter",
      "remedy": "Replace the hydraulic filter",
      "component_name": "Hydraulic filter",
      "equipment_reference": "Hydraulic Pump",
      "source_chunk_id": "chunk_001",
      "confidence_score": 0.9,
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
    assert len(result.suppliers) == 1
    assert result.suppliers[0].supplier_id.startswith("supplier_")
    assert result.suppliers[0].source_chunk_id == second_chunk.chunk_id
    assert len(result.contact_points) == 1
    assert result.contact_points[0].contact_point_id.startswith("contact_point_")
    assert result.contact_points[0].value == "service@example.com"
    assert result.contact_points[0].owner_name == "Example Manufacturer"
    assert result.contact_points[0].source_chunk_id == second_chunk.chunk_id
    assert len(result.procedures) == 1
    assert result.procedures[0].procedure_id.startswith("procedure_")
    assert result.procedures[0].procedure_type == ProcedureType.INSTALLATION
    assert result.procedures[0].steps == [
        "Depressurize the line.",
        "Remove the old filter.",
        "Install the new filter.",
    ]
    assert result.procedures[0].equipment_id == result.equipment[0].equipment_id
    assert len(result.specifications) == 1
    assert result.specifications[0].specification_id.startswith("specification_")
    assert result.specifications[0].parameter == "Pressure rating"
    assert result.specifications[0].unit == "bar"
    assert len(result.safety_warnings) == 1
    assert result.safety_warnings[0].safety_warning_id.startswith("safety_warning_")
    assert result.safety_warnings[0].warning_type == "danger"
    assert len(result.maintenance_intervals) == 1
    assert result.maintenance_intervals[0].maintenance_interval_id.startswith(
        "maintenance_interval_"
    )
    assert (
        result.maintenance_intervals[0].maintenance_task_id
        == result.maintenance_tasks[0].task_id
    )
    assert len(result.troubleshooting_entries) == 1
    assert result.troubleshooting_entries[0].troubleshooting_id.startswith(
        "troubleshooting_"
    )
    assert result.troubleshooting_entries[0].symptom == "Pump fails to build pressure"
    assert result.troubleshooting_entries[0].cause == "Worn hydraulic filter"
    assert (
        result.troubleshooting_entries[0].equipment_id == result.equipment[0].equipment_id
    )
    assert result.maintenance_tasks[0].source.page_start == sample_chunk.source.page_start
    assert result.spare_parts[0].source.page_start == second_chunk.source.page_start
    assert fake_extraction_service.saved_results == [result]
    assert validator.calls == [result]
    assert sample_chunk.content in fake_llm_service.calls[0]["prompt"]
    assert second_chunk.content in fake_llm_service.calls[0]["prompt"]
    assert fake_llm_service.calls[0]["model"] == "qwen3:8b"
    assert fake_llm_service.calls[0]["temperature"] == 0.0
    assert fake_llm_service.calls[0]["json_mode"] is True
