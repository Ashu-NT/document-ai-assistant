"""Equivalence proofs + content checks for the candidate-routing diagnostic
capture added across ExtractionCandidateLLMRouter.route(),
ExtractionCandidateSelector.select_for_chunk(), resolve_requested_types(),
ExtractionPromptNarrowingService.build_prompt(), and build_extraction_plan().

Every "with sink" test below passes a *fresh* diagnostics list and re-runs
the SAME call "without sink" (sink=None/omitted), asserting the return
value is identical either way. This is the behavior-equivalence guarantee
this diagnostic capture is required to uphold (task requirement 6): turning
on observation must never change a routing decision, a candidate set, or a
rendered prompt.
"""

import json

from src.application.prompts.extraction import (
    CombinedExtractionPromptBuilder,
    ExtractionPromptType,
)
from src.application.prompts.extraction.narrowed import ExtractionNarrowedPromptBuilder
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.candidates.extraction_candidate_llm_router import (
    ExtractionCandidateLLMRouter,
)
from src.application.workflows.extraction.candidates.extraction_candidate_routing_cache import (
    InMemoryRoutingDecisionCache,
)
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
)
from src.application.workflows.extraction.candidates.extraction_prompt_narrowing_service import (
    ExtractionPromptNarrowingService,
    resolve_requested_types,
)
from src.application.workflows.extraction.specialized.extraction_plan import (
    build_extraction_plan,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk


class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[str] = []

    def generate(self, prompt, model=None, response_schema=None, num_predict=None):
        self.calls.append(prompt)
        return self.response


def _chunk(
    chunk_id: str = "chunk_001",
    *,
    content: str = "Ambiguous general content.",
    chunk_type: ChunkType = ChunkType.GENERAL,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=chunk_type,
        section_path=["General"],
        source=SourceLocation(page_start=1, page_end=1),
    )


def _batch(chunks: list[DocumentChunk], *, batch_index: int = 1, batch_count: int = 1) -> ExtractionBatch:
    return ExtractionBatch(
        batch_index=batch_index,
        batch_count=batch_count,
        chunks=chunks,
        char_count=sum(len(c.content) for c in chunks),
        word_count=sum(len(c.content.split()) for c in chunks),
    )


class TestRouterEquivalence:
    def test_route_returns_identical_value_with_and_without_sink(self) -> None:
        router = ExtractionCandidateLLMRouter(
            llm_service=FakeLLMService(
                json.dumps({"candidate_types": ["safety_warning", "spare_part"]})
            ),
            enabled=True,
        )
        chunk = _chunk()

        without_sink = router.route(chunk)
        with_sink_result_list: list = []
        with_sink = router.route(chunk, diagnostics_sink=with_sink_result_list)

        assert without_sink == with_sink
        assert len(with_sink_result_list) == 1

    def test_disabled_router_records_available_false_and_never_invokes_llm(self) -> None:
        router = ExtractionCandidateLLMRouter(
            llm_service=FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]})),
            enabled=False,
        )
        sink: list = []

        result = router.route(_chunk(), diagnostics_sink=sink)

        assert result is None
        assert len(sink) == 1
        record = sink[0]
        assert record.available is False
        assert record.invoked_llm is False
        assert record.schema_valid is None
        assert record.resolved_types is None

    def test_empty_content_records_had_content_false_and_never_invokes_llm(self) -> None:
        router = ExtractionCandidateLLMRouter(
            llm_service=FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]})),
            enabled=True,
        )
        sink: list = []

        result = router.route(_chunk(content="   "), diagnostics_sink=sink)

        assert result is None
        record = sink[0]
        assert record.available is True
        assert record.had_content is False
        assert record.invoked_llm is False

    def test_malformed_response_records_invoked_llm_true_schema_valid_false(self) -> None:
        router = ExtractionCandidateLLMRouter(
            llm_service=FakeLLMService("not json at all"),
            enabled=True,
        )
        sink: list = []

        result = router.route(_chunk(), diagnostics_sink=sink)

        assert result is None
        record = sink[0]
        assert record.invoked_llm is True
        assert record.schema_valid is False
        assert record.resolved_types is None

    def test_successful_route_records_sorted_resolved_types(self) -> None:
        router = ExtractionCandidateLLMRouter(
            llm_service=FakeLLMService(
                json.dumps({"candidate_types": ["spare_part", "safety_warning"]})
            ),
            enabled=True,
        )
        sink: list = []

        result = router.route(_chunk(), diagnostics_sink=sink)

        assert result == frozenset(
            {ExtractionPromptType.SAFETY_WARNING, ExtractionPromptType.SPARE_PART}
        )
        record = sink[0]
        assert record.invoked_llm is True
        assert record.schema_valid is True
        # canonical ordering: sorted by .value, regardless of response order
        assert record.resolved_types == ("safety_warning", "spare_part")


class TestSelectorEquivalence:
    def test_select_for_chunk_identical_with_and_without_sink_ungated(self) -> None:
        router = ExtractionCandidateLLMRouter(
            llm_service=FakeLLMService(json.dumps({"candidate_types": ["safety_warning"]})),
            enabled=True,
        )
        selector = ExtractionCandidateSelector(llm_router=router)
        chunk = _chunk(chunk_type=ChunkType.GENERAL)

        without_sink = selector.select_for_chunk(chunk)
        with_sink: list = []
        with_sink_result = selector.select_for_chunk(chunk, diagnostics_sink=with_sink)

        assert without_sink == with_sink_result
        assert len(with_sink) == 1

    def test_select_for_chunk_identical_with_and_without_sink_gated(self) -> None:
        selector = ExtractionCandidateSelector(llm_router=None)
        chunk = _chunk(chunk_type=ChunkType.SAFETY_WARNING, content="Danger: hazard.")

        without_sink = selector.select_for_chunk(chunk)
        with_sink: list = []
        with_sink_result = selector.select_for_chunk(chunk, diagnostics_sink=with_sink)

        assert without_sink == with_sink_result
        record = with_sink[0]
        assert record.is_ungated is False
        assert "safety_warning" in record.deterministic_candidate_types
        assert record.llm_routing is None  # router never consulted for gated chunks

    def test_diagnostics_record_reasons_are_derivable_and_canonically_sorted(self) -> None:
        router = ExtractionCandidateLLMRouter(
            llm_service=FakeLLMService(json.dumps({"candidate_types": ["spare_part"]})),
            enabled=True,
        )
        selector = ExtractionCandidateSelector(llm_router=router)
        chunk = _chunk(chunk_type=ChunkType.GENERAL)
        sink: list = []

        result = selector.select_for_chunk(chunk, diagnostics_sink=sink)

        record = sink[0]
        assert record.requested_types == tuple(sorted(t.value for t in result))
        reasons = dict(record.inclusion_reasons)
        assert reasons[ExtractionPromptType.SPARE_PART.value] == ("llm_router",)
        assert reasons[ExtractionPromptType.IDENTIFIER.value] == ("always",)
        # a type genuinely excluded this time has no contributing source
        assert reasons[ExtractionPromptType.MANUFACTURER.value] == ()
        # dict/tuple is sorted by type_value for stable, diffable output
        values = [value for value, _ in record.inclusion_reasons]
        assert values == sorted(values)

    def test_document_and_batch_identifiers_pass_through_unchanged(self) -> None:
        selector = ExtractionCandidateSelector(llm_router=None)
        chunk = _chunk(chunk_type=ChunkType.SAFETY_WARNING, content="Danger.")
        sink: list = []

        selector.select_for_chunk(
            chunk,
            diagnostics_sink=sink,
            document_id="doc_42",
            batch_index=3,
            batch_count=7,
        )

        record = sink[0]
        assert record.document_id == "doc_42"
        assert record.batch_index == 3
        assert record.batch_count == 7
        assert record.chunk_id == "chunk_001"


class TestRoutingCacheDoesNotAlterCandidateReconciliation:
    """End-to-end, through the real ExtractionCandidateSelector: a cache
    hit must reproduce select_for_chunk's exact prior return value, and
    never make a second LLM call for the same content."""

    def test_cache_hit_reproduces_identical_candidate_reconciliation(self) -> None:
        llm_service = FakeLLMService(
            json.dumps({"candidate_types": ["safety_warning", "spare_part"]})
        )
        cache = InMemoryRoutingDecisionCache()
        router = ExtractionCandidateLLMRouter(
            llm_service=llm_service, enabled=True, cache=cache
        )
        selector = ExtractionCandidateSelector(llm_router=router)
        chunk = _chunk(chunk_type=ChunkType.GENERAL)

        first = selector.select_for_chunk(chunk)
        assert len(llm_service.calls) == 1

        second = selector.select_for_chunk(chunk)

        assert second == first
        assert len(llm_service.calls) == 1  # cache hit - no second LLM call


class TestResolveRequestedTypesEquivalence:
    def test_identical_result_with_and_without_sink(self) -> None:
        selector = ExtractionCandidateSelector(llm_router=None)
        batch = _batch(
            [
                _chunk("c1", chunk_type=ChunkType.SAFETY_WARNING, content="Danger."),
                _chunk("c2", chunk_type=ChunkType.TECHNICAL_SPECIFICATION, content="Spec: 10 bar."),
            ]
        )

        without_sink = resolve_requested_types(batch, selector)
        sink: list = []
        with_sink = resolve_requested_types(
            batch, selector, document_id="doc_001", diagnostics_sink=sink
        )

        assert without_sink == with_sink
        assert len(sink) == 2
        assert {record.chunk_id for record in sink} == {"c1", "c2"}


class TestBuildExtractionPlanEquivalence:
    def test_identical_work_items_with_and_without_diagnostics(self) -> None:
        selector = ExtractionCandidateSelector(llm_router=None)
        batch = _batch(
            [_chunk("c1", chunk_type=ChunkType.SAFETY_WARNING, content="Danger.")]
        )

        plan_without = build_extraction_plan([batch], candidate_selector=selector)
        sink: list = []
        plan_with = build_extraction_plan(
            [batch],
            candidate_selector=selector,
            document_id="doc_001",
            candidate_routing_diagnostics_sink=sink,
        )

        assert plan_without == plan_with
        assert len(sink) == 1


class TestBuildPromptEquivalence:
    def test_rendered_prompt_is_byte_identical_with_and_without_diagnostics(self) -> None:
        selector = ExtractionCandidateSelector(llm_router=None)
        service = ExtractionPromptNarrowingService(
            prompt_builder=CombinedExtractionPromptBuilder(),
            narrowed_prompt_builder=ExtractionNarrowedPromptBuilder(),
            candidate_selector=selector,
            enable_candidate_narrowing=True,
        )
        batch = _batch(
            [_chunk("c1", chunk_type=ChunkType.SAFETY_WARNING, content="Danger: hazard.")]
        )

        prompt_without, types_without = service.build_prompt(
            document_id="doc_001", batch=batch, previous_error=None
        )
        sink: list = []
        prompt_with, types_with = service.build_prompt(
            document_id="doc_001",
            batch=batch,
            previous_error=None,
            candidate_routing_diagnostics_sink=sink,
        )

        assert prompt_without == prompt_with
        assert types_without == types_with
        assert len(sink) == 1
