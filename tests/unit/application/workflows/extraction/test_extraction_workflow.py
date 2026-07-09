import pytest

from src.application.prompts.extraction import IdentifierExtractionPromptBuilder
from src.application.validation.extraction import ExtractionResultValidator
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.extraction.batching import ExtractionChunkBatcher
from src.domain.assets import TableAsset
from src.domain.common import ChunkType
from src.domain.document import DocumentChunk, DocumentSection
from src.domain.extraction import (
    EquipmentInfo,
    ExtractionResult,
    Manufacturer,
    MaintenanceInterval,
    MaintenanceTask,
    Procedure,
    ProcedureType,
    SafetyWarning,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
)
from src.shared.exceptions import SchemaValidationError
from src.shared.execution import ActionResult
from src.shared.ids import IdGenerator


class FakeLLMService:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        activity_context=None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "temperature": temperature,
                "json_mode": json_mode,
                "response_schema": response_schema,
            }
        )
        return self.responses.pop(0)


class FakeExtractionService:
    def __init__(self) -> None:
        self.saved_results = []
        self.replaced_results = []

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

    def replace_extraction_result(
        self,
        result,
        activity_context=None,
    ) -> ActionResult:
        self.replaced_results.append(result)
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
    workflow_kwargs = {"max_attempts": 1, **kwargs}
    workflow = ExtractionWorkflow(
        llm_service=fake_llm_service,
        extraction_service=fake_extraction_service,
        extraction_result_validator=spy_validator,
        id_generator=IdGenerator(),
        prompt_builder=IdentifierExtractionPromptBuilder(),
        extraction_model="qwen3:8b",
        confidence_threshold=0.8,
        require_human_review_default=False,
        **workflow_kwargs,
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


def _empty_extraction_response() -> str:
    return """{
  "confidence_score": 0.8,
  "requires_human_review": false,
  "maintenance_tasks": [],
  "spare_parts": [],
  "equipment": [],
  "manufacturers": []
}"""


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
    fake_llm_service = FakeLLMService(
        [
            '{"candidate_types": ["maintenance_task", "spare_part", "equipment", "manufacturer", "supplier", "contact_point", "procedure", "specification", "safety_warning", "maintenance_interval", "troubleshooting", "identifier"]}',
            _empty_extraction_response(),
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        enable_candidate_narrowing=True,
    )

    workflow.extract(sample_chunk.document_id, [chunk_a, chunk_b])

    prompt = fake_llm_service.calls[1]["prompt"]
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


def make_bare_workflow() -> ExtractionWorkflow:
    workflow, _ = make_workflow(FakeLLMService([]), FakeExtractionService())
    return workflow


def test_has_meaningful_entity_content_false_when_all_content_fields_empty() -> None:
    workflow = make_bare_workflow()
    task = MaintenanceTask(
        task_id="task_001",
        document_id="document_001",
        title="",
        source_chunk_id="chunk_001",
    )

    assert (
        workflow._has_meaningful_entity_content(task, ("title", "description", "interval"))
        is False
    )


def test_has_meaningful_entity_content_true_when_string_field_set() -> None:
    workflow = make_bare_workflow()
    task = MaintenanceTask(
        task_id="task_001",
        document_id="document_001",
        title="Replace filter",
        source_chunk_id="chunk_001",
    )

    assert (
        workflow._has_meaningful_entity_content(task, ("title", "description", "interval"))
        is True
    )


def test_has_meaningful_entity_content_true_for_non_string_field() -> None:
    workflow = make_bare_workflow()
    procedure = Procedure(
        procedure_id="procedure_001",
        document_id="document_001",
        title="",
        equipment_id="equipment_001",
        source_chunk_id="chunk_001",
    )

    assert (
        workflow._has_meaningful_entity_content(
            procedure, ("title", "steps", "component_name", "equipment_id")
        )
        is True
    )


def test_has_meaningful_entity_content_false_for_empty_list_field() -> None:
    workflow = make_bare_workflow()
    procedure = Procedure(
        procedure_id="procedure_001",
        document_id="document_001",
        title="",
        steps=[],
        source_chunk_id="chunk_001",
    )

    assert (
        workflow._has_meaningful_entity_content(
            procedure, ("title", "steps", "component_name", "equipment_id")
        )
        is False
    )


def test_drop_empty_entities_removes_fully_empty_items_across_all_types() -> None:
    workflow = make_bare_workflow()
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

    filtered_result, dropped_count = workflow._drop_empty_entities(result)

    assert [task.task_id for task in filtered_result.maintenance_tasks] == ["task_real"]
    assert filtered_result.spare_parts == []
    assert [
        warning.safety_warning_id for warning in filtered_result.safety_warnings
    ] == ["safety_real"]
    assert dropped_count == 3


def test_drop_empty_entities_keeps_items_with_only_non_content_fields_absent() -> None:
    # An item with a real component_name but no other fields should survive
    # — component_name alone is meaningful content.
    workflow = make_bare_workflow()
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

    filtered_result, dropped_count = workflow._drop_empty_entities(result)

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


def test_extraction_rejects_truncated_json_response(sample_chunk) -> None:
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

    with pytest.raises(SchemaValidationError):
        workflow.extract(sample_chunk.document_id, sample_chunk)


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


# ---------------------------------------------------------------------------
# Table hydration — a chunk referencing a table gets the FULL table markdown
# substituted in, instead of whatever partial row-window the chunker split
# it into, so extraction never sees a table row split across chunks.
# ---------------------------------------------------------------------------


def _make_table_chunk(sample_chunk, *, chunk_id: str, content: str, table_ids: list[str]):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=sample_chunk.chunk_type,
        section_path=sample_chunk.section_path,
        element_ids=sample_chunk.element_ids,
        table_ids=table_ids,
        picture_ids=sample_chunk.picture_ids,
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )


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

    hydrated = ExtractionWorkflow._hydrate_table_chunks([partial_chunk], {"table_001": table})

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

    hydrated = ExtractionWorkflow._hydrate_table_chunks(
        [first_chunk, second_chunk], {"table_001": table}
    )

    assert len(hydrated) == 1
    assert hydrated[0].chunk_id == "chunk_table_1"
    assert "HP-002" in hydrated[0].content


def test_hydrate_table_chunks_leaves_non_table_chunks_unchanged(sample_chunk) -> None:
    hydrated = ExtractionWorkflow._hydrate_table_chunks([sample_chunk], {})

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

    hydrated = ExtractionWorkflow._hydrate_table_chunks([partial_chunk], {"table_001": table})

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

    hydrated = ExtractionWorkflow._hydrate_table_chunks([partial_chunk], {"table_001": table})

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

    hydrated = ExtractionWorkflow._hydrate_table_chunks([partial_chunk], {"table_001": table})

    assert "Spare parts for the hydraulic pump" in hydrated[0].content


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

