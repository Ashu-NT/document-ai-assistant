from src.application.workflows.extraction.extraction_execution_strategy import (
    ExtractionExecutionStrategy,
)
from tests.unit.application.workflows.extraction._test_extraction_workflow_support_part1 import (
    FakeExtractionService,
    FakeLLMService,
    make_workflow,
    _empty_extraction_response,
)


def test_multi_family_propagates_num_ctx_to_the_llm_call(sample_chunk) -> None:
    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service, fake_extraction_service, num_ctx=16384
    )

    workflow.extract("doc_001", [sample_chunk])

    assert fake_llm_service.calls[0]["num_ctx"] == 16384


def test_specialized_family_propagates_num_ctx_to_the_llm_call(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [_empty_extraction_response() for _ in range(3)]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        num_ctx=16384,
    )

    workflow.extract("doc_001", [sample_chunk])

    assert all(call["num_ctx"] == 16384 for call in fake_llm_service.calls)


def test_num_ctx_defaults_from_settings_when_not_explicitly_passed(sample_chunk) -> None:
    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(fake_llm_service, fake_extraction_service)

    workflow.extract("doc_001", [sample_chunk])

    assert fake_llm_service.calls[0]["num_ctx"] == workflow.num_ctx
    assert fake_llm_service.calls[0]["num_ctx"] is not None
