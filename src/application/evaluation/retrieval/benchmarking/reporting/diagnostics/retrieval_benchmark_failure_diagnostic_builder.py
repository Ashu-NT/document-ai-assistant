from src.application.evaluation.retrieval.benchmarking.models.retrieval_benchmark_case_result import (
    RetrievalBenchmarkCaseResult,
)


class RetrievalBenchmarkFailureDiagnosticBuilder:
    def build_failure_reasons(
        self,
        case_result: RetrievalBenchmarkCaseResult,
    ) -> list[str]:
        case = case_result.case
        reasons: list[str] = []

        if not case_result.hit:
            reasons.append(
                "Anchor retrieval did not return the expected evidence."
            )

        if (
            case.expected_rank_target is not None
            and case_result.matched_rank is not None
            and not case_result.meets_expected_rank_target
        ):
            reasons.append(
                "Anchor retrieval found relevant evidence, but later than the "
                f"expected {case.expected_rank_target.value} target "
                f"(matched rank: {case_result.matched_rank})."
            )

        if case.expected_chunk_ids and not any(
            chunk.chunk_id in case.expected_chunk_ids
            for chunk in case_result.returned_chunks
        ):
            reasons.append(
                "Anchor retrieval did not return the resolved expected chunk id."
            )

        if case.expected_section_paths and not case_result.exact_section_path_hit:
            reasons.append(
                "Anchor retrieval missed the expected section path."
            )

        if case.expected_page is not None and not self._has_page_hit(
            case_result.returned_chunks,
            case.expected_page,
        ):
            reasons.append(
                f"Anchor retrieval did not return a chunk covering expected page {case.expected_page}."
            )

        if case_result.context_hit and not case_result.hit:
            reasons.append(
                "Context expansion recovered the expected evidence after the anchor miss."
            )

        if (
            case.expected_section_paths
            and case_result.context_exact_section_path_hit
            and not case_result.exact_section_path_hit
        ):
            reasons.append(
                "Context expansion reached the expected section path even though the anchor results did not."
            )

        if not reasons:
            reasons.append(
                "Anchor retrieval satisfied the benchmark target for this case."
            )

        return reasons

    @staticmethod
    def _has_page_hit(
        returned_chunks,
        expected_page: int,
    ) -> bool:
        return any(
            chunk.covers_page(expected_page)
            for chunk in returned_chunks
        )
