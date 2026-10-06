from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

from src.application.workflows.extraction.extraction_execution_strategy import (
    ExtractionExecutionStrategy,
)
from src.domain.assets import TableAsset


def test_default_execution_strategy_is_multi_family(sample_chunk) -> None:
    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    assert workflow.execution_strategy is ExtractionExecutionStrategy.MULTI_FAMILY


def test_explicit_multi_family_strategy_still_issues_exactly_one_combined_call(
    sample_chunk,
) -> None:
    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        execution_strategy=ExtractionExecutionStrategy.MULTI_FAMILY,
    )

    workflow.extract("doc_001", [sample_chunk])

    assert len(fake_llm_service.calls) == 1


def test_specialized_family_strategy_issues_one_call_per_candidate_family_and_merges(
    sample_chunk,
) -> None:
    # sample_chunk resolves deterministically to exactly
    # {IDENTIFIER, MAINTENANCE_INTERVAL, MAINTENANCE_TASK} under
    # ExtractionCandidateSelector(llm_router=None) -- see
    # test_three_selected_families_produce_three_work_items in
    # specialized/test_extraction_plan.py. The plan sorts families by their
    # string value, so responses must be queued in that same order:
    # "identifier" < "maintenance_interval" < "maintenance_task".
    identifier_response = """{
  "confidence_score": 0.9,
  "identifiers": [
    {"raw_value": "HP-001", "identifier_type": "part_number", "source_chunk_id": "chunk_001"}
  ]
}"""
    maintenance_interval_response = """{
  "confidence_score": 0.9,
  "maintenance_intervals": [
    {"interval": "1000 operating hours", "component_name": "Hydraulic filter", "source_chunk_id": "chunk_001"}
  ]
}"""
    maintenance_task_response = """{
  "confidence_score": 0.9,
  "maintenance_tasks": [
    {"title": "Replace hydraulic filter", "description": "Replace the hydraulic filter.", "source_chunk_id": "chunk_001"}
  ]
}"""
    fake_llm_service = FakeLLMService(
        [
            identifier_response,
            maintenance_interval_response,
            maintenance_task_response,
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
    )

    result = workflow.extract("doc_001", [sample_chunk])

    assert len(fake_llm_service.calls) == 3
    assert len(result.extracted_identifiers) == 1
    assert len(result.maintenance_intervals) == 1
    assert len(result.maintenance_tasks) == 1
    assert result.unresolved_chunk_ids == []
    assert result.unresolved_extraction_work == []


def test_specialized_family_strategy_still_hydrates_table_chunks_before_extraction() -> None:
    # Reuses the same table hydration pathway MULTI_FAMILY already exercises
    # (hydrate_table_chunks runs in extract() before batching, regardless of
    # execution_strategy) -- this test only proves SPECIALIZED_FAMILY does
    # not bypass it.
    from src.domain.common import ChunkType, SourceLocation
    from src.domain.document import DocumentChunk

    document_id = "doc_001"
    table_chunk = DocumentChunk(
        chunk_id="chunk_001",
        document_id=document_id,
        section_id="sec_001",
        content="See table below.",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=["Spare Parts"],
        table_ids=["table_001"],
        source=SourceLocation(page_start=1, page_end=1),
    )
    table_asset = TableAsset(
        table_id="table_001",
        document_id=document_id,
        parent_section_id="sec_001",
        markdown="| Part Number | Description |\n|---|---|\n| HP-001 | Hydraulic filter |",
    )
    identifier_response = '{"confidence_score": 0.9}'
    fake_llm_service = FakeLLMService([identifier_response] * 10)
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
    )

    workflow.extract(
        document_id,
        [table_chunk],
        tables={"table_001": table_asset},
    )

    assert fake_llm_service.calls, "expected at least one specialized call"
    assert any(
        "HP-001" in str(call["prompt"]) for call in fake_llm_service.calls
    ), "hydrated table content should appear in the specialized prompt(s)"
