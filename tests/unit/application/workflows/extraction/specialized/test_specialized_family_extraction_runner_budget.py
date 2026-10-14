from src.application.contracts.ai import LLMGenerationResult
from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.execution_budget import (
    ExtractionExecutionBudget,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.response import ExtractionResponseParser
from src.application.workflows.extraction.specialized.specialized_family_extraction_runner import (
    SpecializedFamilyExtractionRunner,
)
from src.application.workflows.extraction.table_windowing import (
    TableEvidenceWindowBuilder,
    TableWindowActivationPolicy,
)
from src.domain.assets import TableAsset
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.shared.ids import IdGenerator

_HEADER = ["Row ID", "Component", "Description"]
_CANONICAL_CHUNK_ID = "chunk_canonical_table"


class _FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now


class _FixedFamiliesSelector:
    def __init__(self, families: frozenset[ExtractionPromptType]) -> None:
        self.families = families

    def select_for_chunk(self, chunk, **_kwargs):
        return self.families


class _SingleFamilySelector:
    def select_for_chunk(self, chunk, **_kwargs):
        return frozenset({ExtractionPromptType.MAINTENANCE_TASK})


class _SpyFamiliesSelector:
    def __init__(self, families: frozenset[ExtractionPromptType]) -> None:
        self.families = families
        self.calls = 0

    def select_for_chunk(self, chunk, **_kwargs):
        self.calls += 1
        return self.families


class _ClockAdvancingLLMService:
    def __init__(self, clock: _FakeClock, seconds_per_call: float, response: str) -> None:
        self.clock = clock
        self.seconds_per_call = seconds_per_call
        self.response = response
        self.calls = 0

    def generate_with_metadata(
        self,
        prompt: str,
        model: str | None = None,
        activity_context=None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict | None = None,
        num_predict: int | None = None,
    ) -> LLMGenerationResult:
        self.calls += 1
        self.clock.now += self.seconds_per_call
        return LLMGenerationResult(
            text=self.response, provider_name="fake", finish_reason="stop"
        )


def _make_assembler() -> ExtractionResultAssembler:
    support = ExtractionBuilderSupport(
        confidence_threshold=0.5, require_human_review_default=False
    )
    return ExtractionResultAssembler(
        id_generator=IdGenerator(),
        response_parser=ExtractionResponseParser(),
        support=support,
    )


def _make_runner(
    llm_service,
    candidate_selector,
    *,
    windowing_enabled: bool = False,
    rows_per_window: int = 10,
) -> SpecializedFamilyExtractionRunner:
    return SpecializedFamilyExtractionRunner(
        llm_service=llm_service,
        extraction_model="qwen2.5:3b",
        temperature=0.0,
        json_mode=True,
        failure_preview_chars=500,
        max_attempts=1,
        allow_partial_batches=True,
        chunk_batcher=ExtractionChunkBatcher(
            max_chunks_per_batch=18, max_chars_per_batch=100_000
        ),
        candidate_selector=candidate_selector,
        result_assembler=_make_assembler(),
        table_window_activation_policy=TableWindowActivationPolicy(
            enabled=windowing_enabled, rows_per_window=rows_per_window
        ),
        table_window_builder=TableEvidenceWindowBuilder(rows_per_window=rows_per_window),
    )


def test_multiple_families_respect_the_shared_remaining_budget() -> None:
    clock = _FakeClock()
    chunk = DocumentChunk(
        chunk_id="chunk_a",
        document_id="doc_001",
        section_id="sec_001",
        content="Generic maintenance content.",
        chunk_type=ChunkType.GENERAL,
        section_path=["General"],
        source=SourceLocation(page_start=1, page_end=1),
    )
    batch = ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[chunk],
        char_count=len(chunk.content), word_count=5,
    )
    families = frozenset(
        {
            ExtractionPromptType.SPECIFICATION,
            ExtractionPromptType.PROCEDURE,
            ExtractionPromptType.SAFETY_WARNING,
        }
    )
    llm_service = _ClockAdvancingLLMService(
        clock, seconds_per_call=3.0, response='{"confidence_score": 0.9}'
    )
    runner = _make_runner(llm_service, _FixedFamiliesSelector(families))
    budget = ExtractionExecutionBudget.start(5.0, clock=clock)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        budget=budget,
    )

    assert llm_service.calls == 2
    assert len(result.partial_results) == 2
    assert len(result.unresolved_extraction_work) == 1
    assert result.unresolved_chunk_ids == ["chunk_a"]


def test_unlimited_budget_does_not_change_multi_family_behavior() -> None:
    clock = _FakeClock()
    chunk = DocumentChunk(
        chunk_id="chunk_a",
        document_id="doc_001",
        section_id="sec_001",
        content="Generic maintenance content.",
        chunk_type=ChunkType.GENERAL,
        section_path=["General"],
        source=SourceLocation(page_start=1, page_end=1),
    )
    batch = ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[chunk],
        char_count=len(chunk.content), word_count=5,
    )
    families = frozenset(
        {ExtractionPromptType.SPECIFICATION, ExtractionPromptType.PROCEDURE}
    )
    llm_service = _ClockAdvancingLLMService(
        clock, seconds_per_call=3.0, response='{"confidence_score": 0.9}'
    )
    runner = _make_runner(llm_service, _FixedFamiliesSelector(families))
    budget = ExtractionExecutionBudget.start(None, clock=clock)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        budget=budget,
    )

    assert llm_service.calls == 2
    assert len(result.partial_results) == 2
    assert result.unresolved_extraction_work == []


def _make_two_chunk_batches() -> tuple[ExtractionBatch, ExtractionBatch]:
    chunk_a = DocumentChunk(
        chunk_id="chunk_a",
        document_id="doc_001",
        section_id="sec_001",
        content="Generic content A.",
        chunk_type=ChunkType.GENERAL,
        section_path=["General"],
        source=SourceLocation(page_start=1, page_end=1),
    )
    chunk_b = DocumentChunk(
        chunk_id="chunk_b",
        document_id="doc_001",
        section_id="sec_001",
        content="Generic content B.",
        chunk_type=ChunkType.GENERAL,
        section_path=["General"],
        source=SourceLocation(page_start=2, page_end=2),
    )
    batch_1 = ExtractionBatch(
        batch_index=1, batch_count=2, chunks=[chunk_a],
        char_count=len(chunk_a.content), word_count=3,
    )
    batch_2 = ExtractionBatch(
        batch_index=2, batch_count=2, chunks=[chunk_b],
        char_count=len(chunk_b.content), word_count=3,
    )
    return batch_1, batch_2


def test_already_expired_budget_prevents_any_candidate_family_selection_call() -> None:
    clock = _FakeClock(start=100.0)
    batch_1, batch_2 = _make_two_chunk_batches()
    selector = _SpyFamiliesSelector(frozenset({ExtractionPromptType.SPECIFICATION}))
    llm_service = _ClockAdvancingLLMService(
        clock, seconds_per_call=1.0, response='{"confidence_score": 0.9}'
    )
    runner = _make_runner(llm_service, selector)
    budget = ExtractionExecutionBudget.start(5.0, clock=clock)
    clock.now += 10.0

    result = runner.run(
        document_id="doc_001",
        batches=[batch_1, batch_2],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        budget=budget,
    )

    assert selector.calls == 0
    assert llm_service.calls == 0
    assert set(result.unresolved_chunk_ids) == {"chunk_a", "chunk_b"}
    assert len(result.unresolved_extraction_work) == 2
    assert all(
        work.entity_type == "budget_exhausted"
        for work in result.unresolved_extraction_work
    )


def test_budget_expiring_between_batches_stops_further_candidate_selection() -> None:
    clock = _FakeClock()
    batch_1, batch_2 = _make_two_chunk_batches()
    selector = _SpyFamiliesSelector(frozenset({ExtractionPromptType.SPECIFICATION}))
    llm_service = _ClockAdvancingLLMService(
        clock, seconds_per_call=6.0, response='{"confidence_score": 0.9}'
    )
    runner = _make_runner(llm_service, selector)
    budget = ExtractionExecutionBudget.start(5.0, clock=clock)

    result = runner.run(
        document_id="doc_001",
        batches=[batch_1, batch_2],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        budget=budget,
    )

    assert selector.calls == 1
    assert llm_service.calls == 1
    assert result.unresolved_chunk_ids == ["chunk_b"]


def _make_table(row_count: int) -> TableAsset:
    data_rows = [
        [f"ID{n:03d}", f"Component {n}", f"Task {n}"] for n in range(1, row_count + 1)
    ]
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="irrelevant canonical markdown",
        rows=[_HEADER, *data_rows],
    )


def _make_canonical_chunk() -> DocumentChunk:
    return DocumentChunk(
        chunk_id=_CANONICAL_CHUNK_ID,
        document_id="doc_001",
        section_id="sec_001",
        content="full canonical rendering",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["6 Maintenance"],
        table_ids=["table_001"],
        source=SourceLocation(page_start=67, page_end=68),
    )


def test_table_windows_respect_the_shared_remaining_budget() -> None:
    clock = _FakeClock()
    table = _make_table(30)  # rows_per_window=10 -> 3 windows
    canonical_chunk = _make_canonical_chunk()
    batch = ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[canonical_chunk],
        char_count=len(canonical_chunk.content), word_count=10,
    )
    llm_service = _ClockAdvancingLLMService(
        clock,
        seconds_per_call=3.0,
        response='{"confidence_score": 0.9, "maintenance_tasks": []}',
    )
    runner = _make_runner(
        llm_service, _SingleFamilySelector(), windowing_enabled=True, rows_per_window=10
    )
    budget = ExtractionExecutionBudget.start(5.0, clock=clock)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        tables={"table_001": table},
        budget=budget,
    )

    assert llm_service.calls == 2
    assert result.unresolved_chunk_ids == [_CANONICAL_CHUNK_ID]
    assert len(result.unresolved_extraction_work) == 1
    skipped_window = result.unresolved_extraction_work[0]
    assert skipped_window.row_start == 21
    assert skipped_window.row_end == 30
