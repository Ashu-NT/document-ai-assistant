import json

from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
)
from src.application.workflows.extraction.extraction_result_assembler import (
    ExtractionResultAssembler,
)
from src.application.workflows.extraction.response import ExtractionResponseParser
from src.application.workflows.extraction.specialized.specialized_family_extraction_runner import (
    SpecializedFamilyExtractionRunner,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.domain.extraction import UnresolvedExtractionWork
from src.shared.ids import IdGenerator


class FakeRoutingLLMService:
    """Returns a pre-wired response keyed by which family's schema key
    appears in the prompt -- a reasonable test double because the
    specialized executor's prompt is genuinely family-scoped (already
    verified by test_specialized_extraction_batch_executor.py), so routing
    on that key is routing on the actual requested family, not a fake
    shortcut."""

    def __init__(self, *, family_responses: dict[str, str]) -> None:
        self.family_responses = family_responses
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
        for family_key, response in self.family_responses.items():
            if family_key in prompt:
                return response
        raise AssertionError(f"no matching family response configured for prompt: {prompt[:200]}")


def _make_chunk(chunk_id: str, content: str, chunk_type: ChunkType) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=chunk_type,
        section_path=["General"],
        source=SourceLocation(page_start=1, page_end=1),
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
    llm_service: FakeRoutingLLMService,
    *,
    max_attempts: int = 1,
    allow_partial_batches: bool = True,
) -> SpecializedFamilyExtractionRunner:
    chunk_batcher = ExtractionChunkBatcher(
        max_chunks_per_batch=10, max_chars_per_batch=100_000
    )
    return SpecializedFamilyExtractionRunner(
        llm_service=llm_service,
        extraction_model="qwen2.5:3b",
        temperature=0.0,
        json_mode=True,
        failure_preview_chars=500,
        max_attempts=max_attempts,
        allow_partial_batches=allow_partial_batches,
        chunk_batcher=chunk_batcher,
        candidate_selector=ExtractionCandidateSelector(llm_router=None),
        result_assembler=_make_assembler(),
    )


def test_results_from_multiple_specialized_calls_merge_into_one_run_result() -> None:
    chunk = _make_chunk("c1", "Danger: crushing hazard.", ChunkType.SAFETY_WARNING)
    batch = ExtractionBatch(
        batch_index=1,
        batch_count=1,
        chunks=[chunk],
        char_count=len(chunk.content),
        word_count=len(chunk.content.split()),
    )
    identifier_response = json.dumps(
        {
            "confidence_score": 0.9,
            "identifiers": [
                {
                    "raw_value": "HP-001",
                    "identifier_type": "part_number",
                    "source_chunk_id": "c1",
                }
            ],
        }
    )
    safety_warning_response = json.dumps(
        {
            "confidence_score": 0.9,
            "safety_warnings": [
                {
                    "warning_type": "crushing",
                    "message": "Crushing hazard near moving parts.",
                    "source_chunk_id": "c1",
                }
            ],
        }
    )
    llm_service = FakeRoutingLLMService(
        family_responses={
            '"identifiers":': identifier_response,
            '"safety_warnings":': safety_warning_response,
        }
    )
    runner = _make_runner(llm_service)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
    )

    assert len(result.partial_results) == 2
    all_identifiers = [
        identifier
        for partial in result.partial_results
        for identifier in partial.extracted_identifiers
    ]
    all_safety_warnings = [
        warning
        for partial in result.partial_results
        for warning in partial.safety_warnings
    ]
    assert len(all_identifiers) == 1
    assert len(all_safety_warnings) == 1
    assert result.unresolved_chunk_ids == []
    assert result.unresolved_extraction_work == []


def test_one_family_failure_does_not_discard_another_familys_success() -> None:
    chunk = _make_chunk("c1", "Danger: crushing hazard.", ChunkType.SAFETY_WARNING)
    batch = ExtractionBatch(
        batch_index=1,
        batch_count=1,
        chunks=[chunk],
        char_count=len(chunk.content),
        word_count=len(chunk.content.split()),
    )
    identifier_response = json.dumps(
        {
            "confidence_score": 0.9,
            "identifiers": [
                {
                    "raw_value": "HP-001",
                    "identifier_type": "part_number",
                    "source_chunk_id": "c1",
                }
            ],
        }
    )
    llm_service = FakeRoutingLLMService(
        family_responses={
            '"identifiers":': identifier_response,
            # Deliberately malformed JSON -- always fails schema parsing,
            # regardless of attempt count.
            '"safety_warnings":': "not valid json {{{",
        }
    )
    runner = _make_runner(llm_service, max_attempts=1, allow_partial_batches=True)

    result = runner.run(
        document_id="doc_001",
        batches=[batch],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
    )

    # The successful IDENTIFIER extraction must survive even though
    # SAFETY_WARNING failed for the same chunk.
    assert len(result.partial_results) == 1
    assert len(result.partial_results[0].extracted_identifiers) == 1
    assert not result.partial_results[0].safety_warnings

    # Unresolved state must be truthful and attributable to the failing
    # family specifically, not overload the plain chunk-id list alone.
    assert result.unresolved_chunk_ids == ["c1"]
    assert result.unresolved_extraction_work == [
        UnresolvedExtractionWork(chunk_id="c1", entity_type="safety_warning")
    ]
    assert result.attempted_chunk_ids.count("c1") == 2


def test_duplicate_identifier_across_two_batches_is_not_collapsed_by_the_runner() -> None:
    # The runner itself does not dedupe across work items -- that is
    # ExtractionResultMerger's job once ExtractionWorkflow merges
    # partial_results, exactly as it already does for MULTI_FAMILY. This
    # test documents/locks that boundary.
    chunk_one = _make_chunk("c1", "Danger: crushing hazard.", ChunkType.SAFETY_WARNING)
    chunk_two = _make_chunk("c2", "Caution: hot surface.", ChunkType.SAFETY_WARNING)
    batch_one = ExtractionBatch(
        batch_index=1,
        batch_count=2,
        chunks=[chunk_one],
        char_count=len(chunk_one.content),
        word_count=len(chunk_one.content.split()),
    )
    batch_two = ExtractionBatch(
        batch_index=2,
        batch_count=2,
        chunks=[chunk_two],
        char_count=len(chunk_two.content),
        word_count=len(chunk_two.content.split()),
    )
    identifier_response = json.dumps(
        {
            "confidence_score": 0.9,
            "identifiers": [
                {
                    "raw_value": "HP-001",
                    "identifier_type": "part_number",
                    "source_chunk_id": None,
                }
            ],
        }
    )
    safety_warning_response = json.dumps({"confidence_score": 0.9, "safety_warnings": []})
    llm_service = FakeRoutingLLMService(
        family_responses={
            '"identifiers":': identifier_response,
            '"safety_warnings":': safety_warning_response,
        }
    )
    runner = _make_runner(llm_service)

    result = runner.run(
        document_id="doc_001",
        batches=[batch_one, batch_two],
        activity_context=None,
        progress_callback=None,
        diagnostics_sink=[],
    )

    all_identifiers = [
        identifier
        for partial in result.partial_results
        for identifier in partial.extracted_identifiers
    ]
    assert len(all_identifiers) == 2
