from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)
from src.application.evaluation.retrieval.benchmarking.resolution.matching.retrieval_benchmark_candidate_content import (
    detect_candidate_role,
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
            role=detect_candidate_role(chunk.content),
            content_text=chunk.content,
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

    @classmethod
    def _section_match_score(
        cls,
        benchmark_case: RetrievalBenchmarkCase,
        chunk: DocumentChunk,
    ) -> tuple[float, bool]:
        chunk_segments = normalize_path_segments(chunk.section_path)
        expected_paths = benchmark_case.expected_section_paths or [
            benchmark_case.expected_section_path
        ]
        if not expected_paths or not chunk_segments:
            return 0.0, False

        best_score = 0.0
        best_exact_match = False
        for expected_path in expected_paths:
            score, exact_match = cls._path_match_score(
                expected_path,
                chunk_segments,
            )
            if exact_match:
                return score, True
            if score > best_score:
                best_score = score
                best_exact_match = exact_match

        return best_score, best_exact_match

    @staticmethod
    def _path_match_score(
        expected_path: list[str],
        chunk_segments: list[str],
    ) -> tuple[float, bool]:
        expected_segments = normalize_path_segments(expected_path)
        if not expected_segments or not chunk_segments:
            return 0.0, False

        expected_text = " > ".join(expected_segments)
        chunk_text = " > ".join(chunk_segments)

        if expected_text == chunk_text:
            return 3.0, True

        if RetrievalBenchmarkChunkMatcher._is_path_prefix_match(
            expected_segments,
            chunk_segments,
        ):
            return 2.0, False

        shared_tail_length = RetrievalBenchmarkChunkMatcher._shared_tail_length(
            expected_segments,
            chunk_segments,
        )
        if shared_tail_length >= 2:
            return 1.5, False

        if expected_segments[-1] == chunk_segments[-1]:
            return 1.0, False

        if (
            expected_segments[-1] in chunk_text
            or chunk_segments[-1] in expected_text
        ):
            return 0.5, False

        return 0.0, False

    @staticmethod
    def _is_path_prefix_match(
        expected_segments: list[str],
        chunk_segments: list[str],
    ) -> bool:
        minimum_length = min(len(expected_segments), len(chunk_segments))
        if minimum_length == 0:
            return False
        return expected_segments[:minimum_length] == chunk_segments[:minimum_length]

    @staticmethod
    def _shared_tail_length(
        expected_segments: list[str],
        chunk_segments: list[str],
    ) -> int:
        shared_length = 0
        for expected_segment, chunk_segment in zip(
            reversed(expected_segments),
            reversed(chunk_segments),
        ):
            if expected_segment != chunk_segment:
                break
            shared_length += 1
        return shared_length

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
