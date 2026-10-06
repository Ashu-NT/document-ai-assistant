from dataclasses import replace

from src.domain.extraction import ExtractionCompletenessStatus


def test_extraction_result_has_results(sample_extraction_result) -> None:
    assert sample_extraction_result.has_results()


def test_extraction_result_counts_tasks(sample_extraction_result) -> None:
    assert sample_extraction_result.task_count() == 1


def test_extraction_result_counts_spare_parts(sample_extraction_result) -> None:
    assert sample_extraction_result.spare_part_count() == 1


# -- completeness_status / is_complete / is_partial / is_failed / has_unresolved_chunks --


def test_all_requested_chunks_processed_is_complete(sample_extraction_result) -> None:
    result = replace(
        sample_extraction_result,
        attempted_chunk_ids=["chunk_1", "chunk_2"],
        unresolved_chunk_ids=[],
    )

    assert result.completeness_status is ExtractionCompletenessStatus.COMPLETE
    assert result.is_complete is True
    assert result.is_partial is False
    assert result.is_failed is False
    assert result.has_unresolved_chunks is False


def test_zero_extracted_entities_with_no_unresolved_chunks_is_complete() -> None:
    """A legitimate document/scope with nothing extractable must still be
    COMPLETE - completeness is never inferred from entity counts."""
    result = _bare_result(attempted_chunk_ids=["chunk_1"], unresolved_chunk_ids=[])

    assert result.has_results() is False
    assert result.completeness_status is ExtractionCompletenessStatus.COMPLETE
    assert result.is_complete is True


def test_some_successful_and_some_unresolved_chunks_is_partial(
    sample_extraction_result,
) -> None:
    result = replace(
        sample_extraction_result,
        attempted_chunk_ids=["chunk_1", "chunk_2", "chunk_3"],
        unresolved_chunk_ids=["chunk_3"],
    )

    assert result.completeness_status is ExtractionCompletenessStatus.PARTIAL
    assert result.is_partial is True
    assert result.is_complete is False
    assert result.is_failed is False
    assert result.has_unresolved_chunks is True


def test_extracted_entities_present_with_unresolved_chunks_is_still_partial(
    sample_extraction_result,
) -> None:
    """Having some extracted entities does not imply COMPLETE if unresolved
    chunks remain - status is derived from chunk bookkeeping only."""
    result = replace(
        sample_extraction_result,
        attempted_chunk_ids=["chunk_1", "chunk_2"],
        unresolved_chunk_ids=["chunk_2"],
    )

    assert result.has_results() is True
    assert result.completeness_status is ExtractionCompletenessStatus.PARTIAL
    assert result.is_complete is False


def test_all_requested_chunks_unresolved_is_failed(sample_extraction_result) -> None:
    result = replace(
        sample_extraction_result,
        attempted_chunk_ids=["chunk_1", "chunk_2"],
        unresolved_chunk_ids=["chunk_1", "chunk_2"],
    )

    assert result.completeness_status is ExtractionCompletenessStatus.FAILED
    assert result.is_failed is True
    assert result.is_complete is False
    assert result.is_partial is False
    assert result.has_unresolved_chunks is True


def test_status_cannot_contradict_unresolved_chunk_ids(sample_extraction_result) -> None:
    """completeness_status is a derived property, never an independently
    settable field - it is mathematically impossible for it to disagree
    with attempted_chunk_ids/unresolved_chunk_ids because it is computed
    from them on every access, with no cached/stored state to drift."""
    complete = replace(
        sample_extraction_result, attempted_chunk_ids=["c1"], unresolved_chunk_ids=[]
    )
    partial = replace(
        sample_extraction_result,
        attempted_chunk_ids=["c1", "c2"],
        unresolved_chunk_ids=["c2"],
    )
    failed = replace(
        sample_extraction_result,
        attempted_chunk_ids=["c1"],
        unresolved_chunk_ids=["c1"],
    )

    for result in (complete, partial, failed):
        assert bool(result.unresolved_chunk_ids) == (not result.is_complete)
        # completeness_status is recomputed from the live lists every time,
        # not cached - mutating the lists after construction changes it too.
        before = result.completeness_status
        result.unresolved_chunk_ids = []
        assert result.completeness_status is ExtractionCompletenessStatus.COMPLETE
        if before is not ExtractionCompletenessStatus.COMPLETE:
            assert result.completeness_status != before


def test_existing_attempted_and_unresolved_chunk_ids_unchanged_by_the_new_properties(
    sample_extraction_result,
) -> None:
    """Regression guard: adding completeness_status must not alter the raw
    attempted_chunk_ids/unresolved_chunk_ids lists themselves."""
    result = replace(
        sample_extraction_result,
        attempted_chunk_ids=["chunk_1", "chunk_2"],
        unresolved_chunk_ids=["chunk_2"],
    )

    _ = result.completeness_status
    _ = result.is_complete
    _ = result.is_partial
    _ = result.is_failed
    _ = result.has_unresolved_chunks

    assert result.attempted_chunk_ids == ["chunk_1", "chunk_2"]
    assert result.unresolved_chunk_ids == ["chunk_2"]


def test_entity_outputs_unchanged_by_completeness_status(sample_extraction_result) -> None:
    """Regression guard: reading completeness_status must not mutate or
    otherwise affect any entity list."""
    before_tasks = list(sample_extraction_result.maintenance_tasks)
    before_parts = list(sample_extraction_result.spare_parts)

    _ = sample_extraction_result.completeness_status

    assert sample_extraction_result.maintenance_tasks == before_tasks
    assert sample_extraction_result.spare_parts == before_parts


def test_completeness_status_is_deterministic_and_repeatable(sample_extraction_result) -> None:
    result = replace(
        sample_extraction_result,
        attempted_chunk_ids=["chunk_1", "chunk_2"],
        unresolved_chunk_ids=["chunk_2"],
    )

    first = result.completeness_status
    second = result.completeness_status

    assert first is second is ExtractionCompletenessStatus.PARTIAL
    assert first == ExtractionCompletenessStatus.PARTIAL
    assert first.value == "partial"


def _bare_result(*, attempted_chunk_ids, unresolved_chunk_ids):
    from src.domain.extraction import ExtractionResult

    return ExtractionResult(
        extraction_id="extraction_bare",
        document_id="doc_bare",
        attempted_chunk_ids=attempted_chunk_ids,
        unresolved_chunk_ids=unresolved_chunk_ids,
    )
