from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_batch_retry_coordinator import (
    ExtractionBatchRetryCoordinator,
)
from src.domain.extraction import ExtractionResult
from src.shared.exceptions import LLMProviderError


def _batch() -> ExtractionBatch:
    return ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[], char_count=10, word_count=2
    )


class _FailThenSucceedExecutor:
    def __init__(self, fail_times: int) -> None:
        self.fail_times = fail_times
        self.calls = 0

    def execute_once(self, *, document_id, batch, activity_context, progress_callback,
                      previous_error, diagnostics_sink, candidate_routing_diagnostics_sink=None, tables=None):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise LLMProviderError(
                "boom", details={"failure_kind": "read_timeout"}
            )
        return ExtractionResult(extraction_id="ext_1", document_id=document_id)


class _AlwaysFailExecutor:
    def __init__(self) -> None:
        self.calls = 0

    def execute_once(self, *, document_id, batch, activity_context, progress_callback,
                      previous_error, diagnostics_sink, candidate_routing_diagnostics_sink=None, tables=None):
        self.calls += 1
        raise LLMProviderError("boom", details={"failure_kind": "read_timeout"})


def test_llm_provider_error_is_retried_up_to_max_attempts() -> None:
    executor = _FailThenSucceedExecutor(fail_times=1)
    coordinator = ExtractionBatchRetryCoordinator(
        max_attempts=2,
        allow_partial_batches=False,
        chunk_batcher=None,
        batch_executor=executor,
    )

    outcome = coordinator.run(
        document_id="doc_1",
        batch=_batch(),
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
    )

    assert executor.calls == 2
    assert len(outcome.partial_results) == 1


def test_llm_provider_error_exhausts_retries_and_raises_when_not_allowing_partial() -> None:
    executor = _AlwaysFailExecutor()
    coordinator = ExtractionBatchRetryCoordinator(
        max_attempts=2,
        allow_partial_batches=False,
        chunk_batcher=None,
        batch_executor=executor,
    )

    import pytest

    with pytest.raises(LLMProviderError):
        coordinator.run(
            document_id="doc_1",
            batch=_batch(),
            activity_context=None,
            progress_callback=None,
            diagnostics_sink=[],
        )

    assert executor.calls == 2


def test_llm_provider_error_marks_unresolved_when_partial_batches_allowed_single_chunk() -> None:
    executor = _AlwaysFailExecutor()
    coordinator = ExtractionBatchRetryCoordinator(
        max_attempts=2,
        allow_partial_batches=True,
        chunk_batcher=None,
        batch_executor=executor,
    )

    outcome = coordinator.run(
        document_id="doc_1",
        batch=_batch(),
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
    )

    assert executor.calls == 2
    assert outcome.unresolved_chunk_ids == []
    assert outcome.partial_results == []


def test_retries_do_not_exceed_max_attempts_even_on_repeated_failure() -> None:
    executor = _AlwaysFailExecutor()
    coordinator = ExtractionBatchRetryCoordinator(
        max_attempts=3,
        allow_partial_batches=True,
        chunk_batcher=None,
        batch_executor=executor,
    )

    coordinator.run(
        document_id="doc_1",
        batch=_batch(),
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
    )

    assert executor.calls == 3
