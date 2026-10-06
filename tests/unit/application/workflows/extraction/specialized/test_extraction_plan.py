import inspect

from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.candidates.extraction_candidate_selector import (
    ExtractionCandidateSelector,
)
from src.application.workflows.extraction.specialized.extraction_plan import (
    ExtractionPlan,
    ExtractionWorkItem,
    build_extraction_plan,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk


def _make_chunk(
    chunk_id: str,
    content: str,
    chunk_type: ChunkType,
    section_path: list[str] | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=chunk_type,
        section_path=section_path or ["General"],
        source=SourceLocation(page_start=1, page_end=1),
    )


def _make_batch(
    chunks: list[DocumentChunk], *, batch_index: int = 1, batch_count: int = 1
) -> ExtractionBatch:
    return ExtractionBatch(
        batch_index=batch_index,
        batch_count=batch_count,
        chunks=chunks,
        char_count=sum(len(chunk.content) for chunk in chunks),
        word_count=sum(len(chunk.content.split()) for chunk in chunks),
    )


def _selector() -> ExtractionCandidateSelector:
    return ExtractionCandidateSelector(llm_router=None)


def test_build_extraction_plan_signature_has_no_golden_expectation_parameter() -> None:
    """Deterministic guard for task requirement: the planner must never be
    given access to golden/expected extraction data -- it only ever takes
    the batches it was asked to extract from and the (existing, production)
    candidate selector."""
    params = set(inspect.signature(build_extraction_plan).parameters)
    assert params == {"batches", "candidate_selector"}


def test_one_selected_family_produces_exactly_one_work_item() -> None:
    # CERTIFICATION_INFO chunks map to an empty candidate set in
    # _CHUNK_TYPE_CANDIDATES -- IDENTIFIER is the only always-on candidate,
    # and this content/section_path trips no cross-signal keyword/regex, so
    # exactly one family (IDENTIFIER) is selected.
    chunk = _make_chunk(
        "c1",
        "This certificate is valid for five years from issue.",
        ChunkType.CERTIFICATION_INFO,
        section_path=["Certification Info"],
    )
    batch = _make_batch([chunk])

    plan = build_extraction_plan([batch], candidate_selector=_selector())

    assert len(plan.work_items) == 1
    assert plan.work_items[0] == ExtractionWorkItem(
        entity_type=ExtractionPromptType.IDENTIFIER, batch=batch
    )


def test_three_selected_families_produce_three_work_items(sample_chunk) -> None:
    # sample_chunk is a MAINTENANCE_INTERVAL chunk whose content ("Replace
    # hydraulic filter every 1000 operating hours.") resolves to exactly
    # {MAINTENANCE_TASK, MAINTENANCE_INTERVAL, IDENTIFIER} -- no other
    # cross-signal keyword/regex in it fires.
    batch = _make_batch([sample_chunk])

    plan = build_extraction_plan([batch], candidate_selector=_selector())

    assert len(plan.work_items) == 3
    assert {item.entity_type for item in plan.work_items} == {
        ExtractionPromptType.MAINTENANCE_TASK,
        ExtractionPromptType.MAINTENANCE_INTERVAL,
        ExtractionPromptType.IDENTIFIER,
    }
    assert all(item.batch is batch for item in plan.work_items)


def test_work_item_batch_chunk_ids_and_order_survive_unchanged() -> None:
    chunks = [
        _make_chunk("c1", "Danger: hazard present.", ChunkType.SAFETY_WARNING),
        _make_chunk("c2", "Caution advised near moving parts.", ChunkType.SAFETY_WARNING),
    ]
    batch = _make_batch(chunks)

    plan = build_extraction_plan([batch], candidate_selector=_selector())

    assert plan.work_items
    for item in plan.work_items:
        assert item.batch.chunk_ids == ["c1", "c2"]
        assert item.batch.chunks == chunks


def test_build_extraction_plan_is_deterministic_across_repeated_calls() -> None:
    chunk = _make_chunk(
        "c1",
        "Replace hydraulic filter every 1000 operating hours.",
        ChunkType.MAINTENANCE_INTERVAL,
    )
    batch = _make_batch([chunk])
    selector = _selector()

    first = build_extraction_plan([batch], candidate_selector=selector)
    second = build_extraction_plan([batch], candidate_selector=selector)

    assert [item.entity_type for item in first.work_items] == [
        item.entity_type for item in second.work_items
    ]


def test_multiple_batches_each_expand_independently() -> None:
    cert_chunk = _make_chunk(
        "c1",
        "This certificate is valid for five years from issue.",
        ChunkType.CERTIFICATION_INFO,
        section_path=["Certification Info"],
    )
    safety_chunk = _make_chunk(
        "c2", "Danger: hazard present.", ChunkType.SAFETY_WARNING
    )
    batch_one = _make_batch([cert_chunk], batch_index=1, batch_count=2)
    batch_two = _make_batch([safety_chunk], batch_index=2, batch_count=2)

    plan = build_extraction_plan(
        [batch_one, batch_two], candidate_selector=_selector()
    )

    batch_one_items = [item for item in plan.work_items if item.batch is batch_one]
    batch_two_items = [item for item in plan.work_items if item.batch is batch_two]
    assert {item.entity_type for item in batch_one_items} == {
        ExtractionPromptType.IDENTIFIER
    }
    assert {item.entity_type for item in batch_two_items} == {
        ExtractionPromptType.SAFETY_WARNING,
        ExtractionPromptType.IDENTIFIER,
    }


def test_empty_batches_produce_an_empty_plan() -> None:
    plan = build_extraction_plan([], candidate_selector=_selector())

    assert plan == ExtractionPlan(work_items=[])
