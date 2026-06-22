import copy

from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)
from src.application.evaluation.retrieval.benchmarking.resolution.matching.retrieval_benchmark_chunk_matcher import (
    RetrievalBenchmarkChunkMatcher,
)
from src.application.evaluation.retrieval.benchmarking.resolution.models import (
    RetrievalBenchmarkCandidateRole,
    RetrievalBenchmarkResolutionDiagnostic,
)
from src.application.evaluation.retrieval.benchmarking.resolution.resolvers.retrieval_benchmark_candidate_canonicalizer import (
    RetrievalBenchmarkCandidateCanonicalizer,
)
from src.domain.document import DocumentGraph


class RetrievalBenchmarkCaseResolver:
    def __init__(
        self,
        *,
        chunk_matcher: RetrievalBenchmarkChunkMatcher | None = None,
        candidate_canonicalizer: RetrievalBenchmarkCandidateCanonicalizer | None = None,
        max_diagnostic_candidates: int = 5,
    ) -> None:
        self.chunk_matcher = chunk_matcher or RetrievalBenchmarkChunkMatcher()
        self.candidate_canonicalizer = (
            candidate_canonicalizer or RetrievalBenchmarkCandidateCanonicalizer()
        )
        self.max_diagnostic_candidates = max_diagnostic_candidates

    def try_resolve_case(
        self,
        benchmark_case: RetrievalBenchmarkCase,
        document_graph: DocumentGraph,
    ) -> tuple[RetrievalBenchmarkCase | None, RetrievalBenchmarkResolutionDiagnostic | None]:
        ordered_chunks = sorted(
            document_graph.chunks.values(),
            key=lambda chunk: chunk.sequence_number,
        )
        candidates = self.chunk_matcher.match_chunks(benchmark_case, ordered_chunks)
        viable_candidates = [
            candidate
            for candidate in candidates
            if candidate.viable
        ]
        canonical_candidates = self.candidate_canonicalizer.canonicalize(
            benchmark_case=benchmark_case,
            candidates=viable_candidates,
        )

        if not canonical_candidates:
            return None, self._build_diagnostic(
                benchmark_case,
                "No final chunk matched the expected section/page/passage signals.",
                candidates,
            )

        best_candidate = canonical_candidates[0]
        second_candidate = (
            canonical_candidates[1]
            if len(canonical_candidates) > 1
            else None
        )
        if (
            second_candidate is not None
            and not self._same_section_family(best_candidate, second_candidate)
            and self._is_ambiguous(
                best_candidate,
                second_candidate,
            )
        ):
            return None, self._build_diagnostic(
                benchmark_case,
                "Multiple final chunks matched this benchmark case ambiguously.",
                canonical_candidates,
            )

        resolved_case = copy.deepcopy(benchmark_case)
        resolved_case.expected_chunk_ids = self._resolved_chunk_ids(
            document_graph=document_graph,
            chunk_id=best_candidate.chunk_id,
        )
        if (
            best_candidate.section_path
            and best_candidate.section_path not in resolved_case.expected_section_paths
        ):
            resolved_case.expected_section_paths.append(
                list(best_candidate.section_path)
            )

        secondary_families = self._secondary_families(
            document_graph=document_graph,
            canonical_candidates=canonical_candidates[1:],
            viable_candidates=viable_candidates,
            primary_section_id=best_candidate.section_id,
        )
        if secondary_families:
            existing_ids = set(resolved_case.expected_chunk_ids)
            for sec_chunk_ids, sec_section_path in secondary_families:
                for cid in sec_chunk_ids:
                    if cid not in existing_ids:
                        resolved_case.expected_chunk_ids.append(cid)
                        existing_ids.add(cid)
                if (
                    sec_section_path
                    and sec_section_path not in resolved_case.expected_section_paths
                ):
                    resolved_case.expected_section_paths.append(sec_section_path)

        return resolved_case, None

    def _build_diagnostic(
        self,
        benchmark_case: RetrievalBenchmarkCase,
        message: str,
        candidates,
    ) -> RetrievalBenchmarkResolutionDiagnostic:
        return RetrievalBenchmarkResolutionDiagnostic(
            case_id=benchmark_case.case_id,
            document_alias=benchmark_case.expected_document_alias,
            file_name=benchmark_case.expected_file_name,
            message=message,
            details={
                "expected_section_path": benchmark_case.expected_section_path_text,
                "expected_page": benchmark_case.expected_page,
                "expected_relevant_passage": benchmark_case.expected_relevant_passage,
            },
            candidate_summaries=list(candidates[: self.max_diagnostic_candidates]),
        )

    @staticmethod
    def _resolved_chunk_ids(
        *,
        document_graph: DocumentGraph,
        chunk_id: str,
    ) -> list[str]:
        best_chunk = document_graph.chunks[chunk_id]
        if best_chunk.chunk_total <= 1 or best_chunk.section_id is None:
            return [chunk_id]

        family_chunks = [
            chunk
            for chunk in document_graph.chunks.values()
            if chunk.section_id == best_chunk.section_id
        ]
        return [
            chunk.chunk_id
            for chunk in sorted(
                family_chunks,
                key=lambda chunk: chunk.sequence_number,
            )
        ]

    @staticmethod
    def _secondary_families(
        *,
        document_graph: DocumentGraph,
        canonical_candidates: list,
        viable_candidates: list,
        primary_section_id: str | None,
        min_passage_overlap: float = 0.5,
    ) -> list[tuple[list[str], list[str]]]:
        seen_section_ids: set[str] = (
            {primary_section_id} if primary_section_id else set()
        )
        result: list[tuple[list[str], list[str]]] = []

        def _add_candidate(candidate) -> None:
            if not candidate.section_id or candidate.section_id in seen_section_ids:
                return
            if candidate.passage_overlap < min_passage_overlap:
                return
            seen_section_ids.add(candidate.section_id)
            chunk_ids = RetrievalBenchmarkCaseResolver._resolved_chunk_ids(
                document_graph=document_graph,
                chunk_id=candidate.chunk_id,
            )
            result.append((chunk_ids, list(candidate.section_path)))

        for candidate in canonical_candidates:
            _add_candidate(candidate)

        # Also scan pre-dedup viable candidates to catch sections collapsed by the
        # canonicalizer. Restricted to ATOMIC_EVIDENCE to avoid companions.
        for candidate in viable_candidates:
            if candidate.role != RetrievalBenchmarkCandidateRole.ATOMIC_EVIDENCE:
                continue
            _add_candidate(candidate)

        return result

    @staticmethod
    def _is_ambiguous(best_candidate, second_candidate) -> bool:
        score_gap = best_candidate.score - second_candidate.score
        overlap_gap = abs(
            best_candidate.passage_overlap - second_candidate.passage_overlap
        )
        return score_gap < 1.0 and overlap_gap <= 0.05

    @staticmethod
    def _same_section_family(best_candidate, second_candidate) -> bool:
        if best_candidate.section_id is None:
            return False
        return best_candidate.section_id == second_candidate.section_id
