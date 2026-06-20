from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)
from src.application.evaluation.retrieval.benchmarking.resolution.matching.text_normalization import (
    normalize_free_text,
    normalize_path_segments,
    tokenize_text,
)
from src.application.evaluation.retrieval.benchmarking.resolution.models import (
    RetrievalBenchmarkResolutionCandidate,
)
from src.domain.document import DocumentChunk


class RetrievalBenchmarkChunkMatcher:
    def __init__(
        self,
        *,
        minimum_passage_overlap: float = 0.35,
    ) -> None:
        self.minimum_passage_overlap = minimum_passage_overlap

    def match_chunks(
        self,
        benchmark_case: RetrievalBenchmarkCase,
        chunks: list[DocumentChunk],
    ) -> list[RetrievalBenchmarkResolutionCandidate]:
        candidates = [
            self._build_candidate(benchmark_case, chunk)
            for chunk in chunks
        ]
        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.score,
                candidate.passage_overlap,
                candidate.exact_passage_match,
                candidate.exact_section_path_match,
                candidate.page_match,
                -candidate.sequence_number,
            ),
            reverse=True,
        )

    def _build_candidate(
        self,
        benchmark_case: RetrievalBenchmarkCase,
        chunk: DocumentChunk,
    ) -> RetrievalBenchmarkResolutionCandidate:
        passage_overlap = self._passage_overlap(
            benchmark_case.expected_relevant_passage,
            chunk.content,
        )
        exact_passage_match = self._exact_passage_match(
            benchmark_case.expected_relevant_passage,
            chunk.content,
        )
        section_match_score, exact_section_path_match = self._section_match_score(
            benchmark_case,
            chunk,
        )
        page_match_score, page_match = self._page_match_score(benchmark_case, chunk)
        passage_score = (4.0 if exact_passage_match else 0.0) + (passage_overlap * 10.0)
        viable = (
            exact_passage_match
            or passage_overlap >= self.minimum_passage_overlap
        ) and (
            page_match
            or section_match_score > 0.0
            or passage_overlap >= 0.7
        )

        return RetrievalBenchmarkResolutionCandidate(
            chunk_id=chunk.chunk_id,
            section_id=chunk.section_id,
            section_path=list(chunk.section_path),
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
            sequence_number=chunk.sequence_number,
            score=passage_score + section_match_score + page_match_score,
            passage_overlap=passage_overlap,
            exact_passage_match=exact_passage_match,
            exact_section_path_match=exact_section_path_match,
            page_match=page_match,
            viable=viable,
            content_preview=self._content_preview(chunk.content),
        )

    @staticmethod
    def _passage_overlap(expected_passage: str | None, content: str) -> float:
        expected_tokens = set(tokenize_text(expected_passage))
        if not expected_tokens:
            return 0.0

        content_tokens = set(tokenize_text(content))
        if not content_tokens:
            return 0.0

        shared_tokens = expected_tokens.intersection(content_tokens)
        return len(shared_tokens) / len(expected_tokens)

    @staticmethod
    def _exact_passage_match(expected_passage: str | None, content: str) -> bool:
        normalized_expected = normalize_free_text(expected_passage)
        normalized_content = normalize_free_text(content)

        if not normalized_expected or not normalized_content:
            return False

        return normalized_expected in normalized_content

    @staticmethod
    def _section_match_score(
        benchmark_case: RetrievalBenchmarkCase,
        chunk: DocumentChunk,
    ) -> tuple[float, bool]:
        expected_segments = normalize_path_segments(
            benchmark_case.expected_section_path
        )
        chunk_segments = normalize_path_segments(chunk.section_path)

        if not expected_segments or not chunk_segments:
            return 0.0, False

        expected_text = " > ".join(expected_segments)
        chunk_text = " > ".join(chunk_segments)

        if expected_text == chunk_text:
            return 3.0, True

        if chunk_text.endswith(expected_text) or expected_text.endswith(chunk_text):
            return 2.0, False

        if expected_segments[-1] == chunk_segments[-1]:
            return 1.0, False

        if expected_segments[-1] in chunk_text:
            return 0.5, False

        return 0.0, False

    @staticmethod
    def _page_match_score(
        benchmark_case: RetrievalBenchmarkCase,
        chunk: DocumentChunk,
    ) -> tuple[float, bool]:
        expected_page = benchmark_case.expected_page
        if expected_page is None:
            return 0.0, False

        page_start = chunk.source.page_start
        page_end = chunk.source.page_end
        if page_start is None and page_end is None:
            return 0.0, False

        resolved_start = page_start if page_start is not None else page_end
        resolved_end = page_end if page_end is not None else page_start
        if resolved_start is None or resolved_end is None:
            return 0.0, False

        if resolved_start <= expected_page <= resolved_end:
            return 2.0, True

        nearest_distance = min(
            abs(expected_page - resolved_start),
            abs(expected_page - resolved_end),
        )
        if nearest_distance == 1:
            return 0.5, False

        return 0.0, False

    @staticmethod
    def _content_preview(content: str, limit: int = 180) -> str:
        preview = " ".join(content.split())
        if len(preview) <= limit:
            return preview
        return f"{preview[: max(0, limit - 3)].rstrip()}..."
