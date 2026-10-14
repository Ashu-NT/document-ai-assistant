import pytest

from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_batch_retry_coordinator import (
    ExtractionBatchRetryCoordinator,
)
from src.application.workflows.extraction.batching.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
from src.application.workflows.extraction.execution_budget import ExtractionExecutionBudget
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.domain.extraction import ExtractionResult
from src.shared.exceptions import LLMProviderError


class _FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class _AlwaysFailExecutor:
    def __init__(self, clock: _FakeClock, seconds_per_call: float) -> None:
        self.clock = clock
        self.seconds_per_call = seconds_per_call
        self.calls = 0
        self.extraction_model = "fake-model"

    def execute_once(self, *, document_id, batch, activity_context, progress_callback,
                      previous_error, diagnostics_sink, candidate_routing_diagnostics_sink=None, tables=None):
        self.calls += 1
        self.clock.advance(self.seconds_per_call)
        raise LLMProviderError("boom", details={"failure_kind": "read_timeout"})


class _SucceedExecutor:
    extraction_model = "fake-model"

    def __init__(self) -> None:
        self.calls = 0

    def execute_once(self, *, document_id, batch, activity_context, progress_callback,
                      previous_error, diagnostics_sink, candidate_routing_diagnostics_sink=None, tables=None):
        self.calls += 1
        return ExtractionResult(extraction_id="ext_1", document_id=document_id)


def _chunk(chunk_id: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        section_id="sec_1",
        content="content",
        chunk_type=ChunkType.GENERAL,
        source=SourceLocation(),
    )


def _batch(chunk_ids: list[str]) -> ExtractionBatch:
    chunks = [_chunk(cid) for cid in chunk_ids]
    return ExtractionBatch(
        batch_index=1, batch_count=1, chunks=chunks,
        char_count=10 * len(chunks), word_count=2 * len(chunks),
    )


def _coordinator(executor, *, max_attempts: int, allow_partial_batches: bool) -> ExtractionBatchRetryCoordinator:
    return ExtractionBatchRetryCoordinator(
        max_attempts=max_attempts,
        allow_partial_batches=allow_partial_batches,
        chunk_batcher=ExtractionChunkBatcher(max_chunks_per_batch=8, max_chars_per_batch=8000),
        batch_executor=executor,
    )


def test_already_expired_budget_prevents_any_inference_call() -> None:
    clock = _FakeClock(start=100.0)
    executor = _AlwaysFailExecutor(clock, seconds_per_call=1.0)
    coordinator = _coordinator(executor, max_attempts=3, allow_partial_batches=True)
    budget = ExtractionExecutionBudget.start(5.0, clock=clock)
    clock.advance(10.0)

    outcome = coordinator.run(
        document_id="doc_1", batch=_batch(["c1"]), activity_context=None,
        progress_callback=None, diagnostics_sink=[], budget=budget,
    )

    assert executor.calls == 0
    assert outcome.unresolved_chunk_ids == ["c1"]
    assert outcome.attempted_chunk_ids == ["c1"]


def test_budget_expiring_mid_attempt_loop_stops_further_attempts() -> None:
    clock = _FakeClock()
    executor = _AlwaysFailExecutor(clock, seconds_per_call=3.0)
    coordinator = _coordinator(executor, max_attempts=5, allow_partial_batches=True)
    budget = ExtractionExecutionBudget.start(5.0, clock=clock)

    outcome = coordinator.run(
        document_id="doc_1", batch=_batch(["c1"]), activity_context=None,
        progress_callback=None, diagnostics_sink=[], budget=budget,
    )

    assert executor.calls == 2
    assert outcome.unresolved_chunk_ids == ["c1"]


def test_chunk_isolation_shares_the_same_deadline_and_cannot_reset_it() -> None:
    clock = _FakeClock()
    executor = _AlwaysFailExecutor(clock, seconds_per_call=3.0)
    coordinator = _coordinator(executor, max_attempts=1, allow_partial_batches=True)
    budget = ExtractionExecutionBudget.start(5.0, clock=clock)

    outcome = coordinator.run(
        document_id="doc_1", batch=_batch(["c1", "c2", "c3"]), activity_context=None,
        progress_callback=None, diagnostics_sink=[], budget=budget,
    )

    assert executor.calls == 2
    assert set(outcome.unresolved_chunk_ids) == {"c1", "c2", "c3"}


def test_unlimited_budget_preserves_existing_successful_extraction_behavior() -> None:
    clock = _FakeClock()
    executor = _SucceedExecutor()
    coordinator = _coordinator(executor, max_attempts=2, allow_partial_batches=True)
    budget = ExtractionExecutionBudget.start(None, clock=clock)

    outcome = coordinator.run(
        document_id="doc_1", batch=_batch(["c1"]), activity_context=None,
        progress_callback=None, diagnostics_sink=[], budget=budget,
    )

    assert executor.calls == 1
    assert len(outcome.partial_results) == 1
    assert outcome.unresolved_chunk_ids == []


def test_no_budget_argument_at_all_preserves_existing_behavior() -> None:
    executor = _AlwaysFailExecutor(_FakeClock(), seconds_per_call=0.0)
    coordinator = _coordinator(executor, max_attempts=2, allow_partial_batches=False)

    with pytest.raises(LLMProviderError):
        coordinator.run(
            document_id="doc_1", batch=_batch(["c1"]), activity_context=None,
            progress_callback=None, diagnostics_sink=[],
        )

    assert executor.calls == 2
