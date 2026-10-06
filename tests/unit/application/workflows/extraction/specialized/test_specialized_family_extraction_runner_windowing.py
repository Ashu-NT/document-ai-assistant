import json

from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.prompts.extraction import ExtractionPromptType
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
from src.domain.extraction import UnresolvedExtractionWork
from src.shared.ids import IdGenerator

_HEADER = ["Row ID", "Component", "Description"]
_CANONICAL_CHUNK_ID = "chunk_canonical_table"


class _SingleFamilyCandidateSelector:
    """Test stub: every chunk resolves to exactly {MAINTENANCE_TASK},
    isolating these tests from the real ExtractionCandidateSelector's
    chunk-type/cross-signal rules (which would add IDENTIFIER and others,
    requiring extra queued responses unrelated to what this test file is
    verifying)."""

    def select_for_chunk(self, chunk):
        return frozenset({ExtractionPromptType.MAINTENANCE_TASK})


class FakeSequentialLLMService:
    """Pops queued responses strictly in call order - the runner's window
    loop is itself strictly ordered (window 1, 2, 3, ...), so this mirrors
    production call order exactly."""

    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[str] = []

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
        self.calls.append(prompt)
        return self.responses.pop(0)


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


def _make_canonical_chunk(content: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=_CANONICAL_CHUNK_ID,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["6 Maintenance"],
        table_ids=["table_001"],
        source=SourceLocation(page_start=67, page_end=68),
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
    *,
    windowing_enabled: bool,
    rows_per_window: int = 10,
    max_attempts: int = 1,
) -> SpecializedFamilyExtractionRunner:
    chunk_batcher = ExtractionChunkBatcher(max_chunks_per_batch=18, max_chars_per_batch=100_000)
    policy = TableWindowActivationPolicy(enabled=windowing_enabled, rows_per_window=rows_per_window)
    return SpecializedFamilyExtractionRunner(
        llm_service=llm_service,
        extraction_model="qwen2.5:3b",
        temperature=0.0,
        json_mode=True,
        failure_preview_chars=500,
        max_attempts=max_attempts,
        allow_partial_batches=True,
        chunk_batcher=chunk_batcher,
        candidate_selector=_SingleFamilyCandidateSelector(),
        result_assembler=_make_assembler(),
        table_window_activation_policy=policy,
        table_window_builder=TableEvidenceWindowBuilder(rows_per_window=rows_per_window),
    )


def _task_response(*titles: str) -> str:
    return json.dumps(
        {
            "confidence_score": 0.9,
            "maintenance_tasks": [
                {"title": title, "source_chunk_id": _CANONICAL_CHUNK_ID}
                for title in titles
            ],
        }
    )


def test_windowing_issues_one_call_per_window_and_preserves_canonical_provenance() -> None:
    table = _make_table(39)
    canonical_chunk = _make_canonical_chunk("full 39-row canonical rendering")
    batch = ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[canonical_chunk],
        char_count=len(canonical_chunk.content), word_count=10,
    )
    llm_service = FakeSequentialLLMService(
        [
            _task_response("Task 1", "Task 2"),
            _task_response("Task 11"),
            _task_response("Task 21"),
            _task_response("Task 31"),
        ]
    )
    runner = _make_runner(llm_service, windowing_enabled=True, rows_per_window=10)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        tables={"table_001": table},
    )

    assert len(llm_service.calls) == 4  # one call per window (39 rows / 10 per window)
    all_tasks = [t for partial in result.partial_results for t in partial.maintenance_tasks]
    assert {t.title for t in all_tasks} == {"Task 1", "Task 2", "Task 11", "Task 21", "Task 31"}
    # Provenance: every resulting task resolves to the REAL canonical chunk
    # id, never a synthetic per-window identifier.
    assert all(t.source_chunk_id == _CANONICAL_CHUNK_ID for t in all_tasks)
    assert result.unresolved_chunk_ids == []
    assert result.unresolved_extraction_work == []


def test_canonical_chunk_object_is_never_mutated() -> None:
    table = _make_table(39)
    canonical_content = "full 39-row canonical rendering - must survive unchanged"
    canonical_chunk = _make_canonical_chunk(canonical_content)
    batch = ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[canonical_chunk],
        char_count=len(canonical_chunk.content), word_count=10,
    )
    llm_service = FakeSequentialLLMService([_task_response("Task 1")] * 4)
    runner = _make_runner(llm_service, windowing_enabled=True, rows_per_window=10)

    runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        tables={"table_001": table},
    )

    # The exact same chunk object instance, untouched.
    assert canonical_chunk.content == canonical_content
    assert canonical_chunk.chunk_id == _CANONICAL_CHUNK_ID
    assert canonical_chunk.table_row_start is None
    assert canonical_chunk.table_row_end is None


def test_non_table_chunk_is_unaffected_by_windowing_being_enabled() -> None:
    plain_chunk = DocumentChunk(
        chunk_id="chunk_plain",
        document_id="doc_001",
        section_id="sec_001",
        content="Check engine oil level periodically.",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=["6 Maintenance"],
        source=SourceLocation(page_start=10, page_end=10),
    )
    batch = ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[plain_chunk],
        char_count=len(plain_chunk.content), word_count=6,
    )
    llm_service = FakeSequentialLLMService([_task_response("Check engine oil level")])
    runner = _make_runner(llm_service, windowing_enabled=True, rows_per_window=10)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        tables={},
    )

    assert len(llm_service.calls) == 1  # no windowing - single normal call
    all_tasks = [t for partial in result.partial_results for t in partial.maintenance_tasks]
    assert [t.title for t in all_tasks] == ["Check engine oil level"]


def test_one_window_failure_does_not_erase_other_windows_success() -> None:
    table = _make_table(20)  # exactly 2 windows of 10
    canonical_chunk = _make_canonical_chunk("full 20-row canonical rendering")
    batch = ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[canonical_chunk],
        char_count=len(canonical_chunk.content), word_count=10,
    )
    llm_service = FakeSequentialLLMService(
        [
            _task_response("Task 1"),
            "not valid json {{{",  # window 2 fails every attempt
        ]
    )
    runner = _make_runner(llm_service, windowing_enabled=True, rows_per_window=10, max_attempts=1)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        tables={"table_001": table},
    )

    all_tasks = [t for partial in result.partial_results for t in partial.maintenance_tasks]
    assert [t.title for t in all_tasks] == ["Task 1"]
    assert result.unresolved_chunk_ids == [_CANONICAL_CHUNK_ID]
    assert result.unresolved_extraction_work == [
        UnresolvedExtractionWork(
            chunk_id=_CANONICAL_CHUNK_ID,
            entity_type="maintenance_task",
            row_start=11,
            row_end=20,
        )
    ]


def test_windowing_disabled_falls_back_to_the_single_unwindowed_call() -> None:
    table = _make_table(39)
    canonical_chunk = _make_canonical_chunk("full 39-row canonical rendering")
    batch = ExtractionBatch(
        batch_index=1, batch_count=1, chunks=[canonical_chunk],
        char_count=len(canonical_chunk.content), word_count=10,
    )
    llm_service = FakeSequentialLLMService([_task_response("Task 1", "Task 2")])
    runner = _make_runner(llm_service, windowing_enabled=False)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
        tables={"table_001": table},
    )

    assert len(llm_service.calls) == 1
    all_tasks = [t for partial in result.partial_results for t in partial.maintenance_tasks]
    assert {t.title for t in all_tasks} == {"Task 1", "Task 2"}
