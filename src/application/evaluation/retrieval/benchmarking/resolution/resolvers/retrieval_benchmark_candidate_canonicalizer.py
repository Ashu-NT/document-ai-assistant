from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)
from src.application.evaluation.retrieval.benchmarking.resolution.matching import (
    normalize_free_text,
    tokenize_text,
)
from src.application.evaluation.retrieval.benchmarking.resolution.matching.retrieval_benchmark_candidate_content import (
    strip_scaffolding_prefixes,
)
from src.application.evaluation.retrieval.benchmarking.resolution.models import (
    RetrievalBenchmarkCandidateRole,
    RetrievalBenchmarkResolutionCandidate,
)


class RetrievalBenchmarkCandidateCanonicalizer:
    _ROLE_PRIORITY = {
        RetrievalBenchmarkCandidateRole.ATOMIC_EVIDENCE: 0,
        RetrievalBenchmarkCandidateRole.CONTEXT_COMPANION: 1,
        RetrievalBenchmarkCandidateRole.ASSET_COMPANION: 2,
        RetrievalBenchmarkCandidateRole.OVERVIEW_COMPANION: 3,
    }

    def canonicalize(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        candidates: list[RetrievalBenchmarkResolutionCandidate],
    ) -> list[RetrievalBenchmarkResolutionCandidate]:
        if not candidates:
            return []

        grouped_candidates: dict[str, list[RetrievalBenchmarkResolutionCandidate]] = {}
        for candidate in candidates:
            family_key = self._family_key(
                benchmark_case=benchmark_case,
                candidate=candidate,
            )
            grouped_candidates.setdefault(family_key, []).append(candidate)

        canonical_candidates: list[RetrievalBenchmarkResolutionCandidate] = []
        for family_candidates in grouped_candidates.values():
            canonical_candidates.extend(
                self._canonical_family_candidates(family_candidates)
            )

        return sorted(canonical_candidates, key=self._candidate_sort_key)

    def _canonical_family_candidates(
        self,
        family_candidates: list[RetrievalBenchmarkResolutionCandidate],
    ) -> list[RetrievalBenchmarkResolutionCandidate]:
        atomic_candidates = [
            candidate
            for candidate in family_candidates
            if candidate.role == RetrievalBenchmarkCandidateRole.ATOMIC_EVIDENCE
        ]
        if not atomic_candidates:
            return [sorted(family_candidates, key=self._candidate_sort_key)[0]]

        atomic_candidates_by_signature: dict[str, list[RetrievalBenchmarkResolutionCandidate]] = {}
        for candidate in atomic_candidates:
            duplicate_signature = self._atomic_duplicate_signature(candidate)
            atomic_candidates_by_signature.setdefault(
                duplicate_signature,
                [],
            ).append(candidate)

        canonical_candidates: list[RetrievalBenchmarkResolutionCandidate] = []
        for signature_candidates in atomic_candidates_by_signature.values():
            if len(signature_candidates) == 1:
                canonical_candidates.append(signature_candidates[0])
                continue

            atomic_candidates_by_section: dict[str, list[RetrievalBenchmarkResolutionCandidate]] = {}
            for candidate in signature_candidates:
                section_key = candidate.section_id or candidate.chunk_id
                atomic_candidates_by_section.setdefault(
                    section_key,
                    [],
                ).append(candidate)

            if len(atomic_candidates_by_section) == 1:
                canonical_candidates.append(
                    sorted(signature_candidates, key=self._candidate_sort_key)[0]
                )
                continue

            canonical_candidates.append(
                sorted(signature_candidates, key=self._candidate_sort_key)[0]
            )

        return sorted(canonical_candidates, key=self._candidate_sort_key)

    def _family_key(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        candidate: RetrievalBenchmarkResolutionCandidate,
    ) -> str:
        evidence_signature = self._evidence_signature(
            expected_passage=benchmark_case.expected_relevant_passage,
            content=candidate.content_text,
        )
        page_span = self._page_span(
            page_start=candidate.page_start,
            page_end=candidate.page_end,
        )
        return "|".join((evidence_signature, page_span))

    def _evidence_signature(
        self,
        *,
        expected_passage: str | None,
        content: str,
    ) -> str:
        normalized_expected = normalize_free_text(expected_passage)
        normalized_content = normalize_free_text(
            strip_scaffolding_prefixes(content)
        )
        if normalized_expected and normalized_expected in normalized_content:
            return normalized_expected

        expected_tokens = tokenize_text(expected_passage)
        if not expected_tokens:
            return normalized_content

        content_tokens = set(tokenize_text(normalized_content))
        overlap_tokens = [
            token
            for token in expected_tokens
            if token in content_tokens
        ]
        return " ".join(overlap_tokens) or normalized_content

    @staticmethod
    def _atomic_duplicate_signature(
        candidate: RetrievalBenchmarkResolutionCandidate,
    ) -> str:
        return normalize_free_text(
            strip_scaffolding_prefixes(candidate.content_text)
        )

    @classmethod
    def _candidate_sort_key(
        cls,
        candidate: RetrievalBenchmarkResolutionCandidate,
    ) -> tuple[int, float, int, float, int]:
        return (
            cls._ROLE_PRIORITY.get(candidate.role, 99),
            -candidate.score,
            -int(candidate.exact_passage_match),
            -candidate.passage_overlap,
            candidate.sequence_number,
        )

    @staticmethod
    def _page_span(
        *,
        page_start: int | None,
        page_end: int | None,
    ) -> str:
        resolved_start = page_start if page_start is not None else page_end
        resolved_end = page_end if page_end is not None else page_start
        if resolved_start is None and resolved_end is None:
            return ""
        if resolved_start is None:
            return str(resolved_end)
        if resolved_end is None:
            return str(resolved_start)
        return f"{resolved_start}-{resolved_end}"
