from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)
from src.application.evaluation.retrieval.benchmarking.resolution.matching.retrieval_benchmark_chunk_matcher import (
    RetrievalBenchmarkChunkMatcher,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk


def _make_chunk(chunk_id: str, content: str, *, section_path=None) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=section_path or ["Maintenance Schedule"],
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_match_chunks_ranks_exact_passage_match_highest() -> None:
    matcher = RetrievalBenchmarkChunkMatcher()
    benchmark_case = RetrievalBenchmarkCase(
        expected_relevant_passage="Replace the hydraulic filter every 1000 hours.",
    )
    exact_chunk = _make_chunk(
        "c_exact",
        "Replace the hydraulic filter every 1000 hours. Additional context here.",
    )
    unrelated_chunk = _make_chunk("c_unrelated", "Check the pump housing for leaks.")

    candidates = matcher.match_chunks(benchmark_case, [unrelated_chunk, exact_chunk])

    assert candidates[0].chunk_id == "c_exact"
    assert candidates[0].exact_passage_match is True
    assert candidates[0].passage_overlap == 1.0


def test_match_chunks_computes_partial_passage_overlap() -> None:
    matcher = RetrievalBenchmarkChunkMatcher()
    benchmark_case = RetrievalBenchmarkCase(
        expected_relevant_passage="replace hydraulic filter every operating hour",
    )
    partial_chunk = _make_chunk("c_partial", "Replace the hydraulic filter regularly.")

    candidates = matcher.match_chunks(benchmark_case, [partial_chunk])

    assert 0.0 < candidates[0].passage_overlap < 1.0
    assert candidates[0].exact_passage_match is False


def test_match_chunks_handles_multiple_chunks_independently() -> None:
    matcher = RetrievalBenchmarkChunkMatcher()
    benchmark_case = RetrievalBenchmarkCase(
        expected_relevant_passage="grease the main shaft bearing",
    )
    chunks = [
        _make_chunk("c1", "Grease the main shaft bearing every 500 hours."),
        _make_chunk("c2", "Inspect the pump housing for visible leaks."),
        _make_chunk("c3", "Grease the main shaft bearing before startup."),
    ]

    candidates = matcher.match_chunks(benchmark_case, chunks)

    assert len(candidates) == 3
    candidate_ids = {c.chunk_id for c in candidates}
    assert candidate_ids == {"c1", "c2", "c3"}
    c1_candidate = next(c for c in candidates if c.chunk_id == "c1")
    c2_candidate = next(c for c in candidates if c.chunk_id == "c2")
    assert c1_candidate.passage_overlap > c2_candidate.passage_overlap


def test_match_chunks_handles_no_expected_passage() -> None:
    matcher = RetrievalBenchmarkChunkMatcher()
    benchmark_case = RetrievalBenchmarkCase(expected_relevant_passage=None)
    chunk = _make_chunk("c1", "Replace the hydraulic filter.")

    candidates = matcher.match_chunks(benchmark_case, [chunk])

    assert candidates[0].passage_overlap == 0.0
    assert candidates[0].exact_passage_match is False
