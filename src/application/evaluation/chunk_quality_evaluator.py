from src.application.evaluation.retrieval_benchmark_case import (
    RetrievalBenchmarkCase,
)
from src.application.evaluation.retrieval_benchmark_case_result import (
    RetrievalBenchmarkCaseResult,
)
from src.application.evaluation.retrieval_benchmark_report import (
    RetrievalBenchmarkReport,
)


class ChunkQualityEvaluator:
    def evaluate(
        self,
        workflow,
        benchmark_cases: list[RetrievalBenchmarkCase],
    ) -> RetrievalBenchmarkReport:
        case_results: list[RetrievalBenchmarkCaseResult] = []

        for benchmark_case in benchmark_cases:
            workflow_result = workflow.run(benchmark_case.query)
            chunks = self._result_chunks(workflow_result)
            returned_chunk_ids = [chunk.chunk_id for chunk in chunks]
            returned_section_paths = [list(chunk.section_path) for chunk in chunks]

            reciprocal_rank = self._reciprocal_rank(
                benchmark_case=benchmark_case,
                returned_chunk_ids=returned_chunk_ids,
                returned_section_paths=returned_section_paths,
            )
            relevant_hits = self._relevant_hits(
                benchmark_case=benchmark_case,
                returned_chunk_ids=returned_chunk_ids,
                returned_section_paths=returned_section_paths,
            )
            case_results.append(
                RetrievalBenchmarkCaseResult(
                    case=benchmark_case,
                    returned_chunk_ids=returned_chunk_ids,
                    returned_section_paths=returned_section_paths,
                    hit=reciprocal_rank > 0.0,
                    reciprocal_rank=reciprocal_rank,
                    relevant_hits=relevant_hits,
                )
            )

        return RetrievalBenchmarkReport(case_results=case_results)

    @staticmethod
    def _result_chunks(workflow_result) -> list:
        if hasattr(workflow_result, "final_chunks"):
            return list(workflow_result.final_chunks)
        if hasattr(workflow_result, "chunks"):
            return list(workflow_result.chunks)
        return []

    def _reciprocal_rank(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        returned_chunk_ids: list[str],
        returned_section_paths: list[list[str]],
    ) -> float:
        for index, chunk_id in enumerate(returned_chunk_ids, start=1):
            if chunk_id in benchmark_case.expected_chunk_ids:
                return 1.0 / index

        for index, section_path in enumerate(returned_section_paths, start=1):
            if section_path in benchmark_case.expected_section_paths:
                return 1.0 / index

        return 0.0

    @staticmethod
    def _relevant_hits(
        *,
        benchmark_case: RetrievalBenchmarkCase,
        returned_chunk_ids: list[str],
        returned_section_paths: list[list[str]],
    ) -> int:
        chunk_hits = sum(
            1
            for chunk_id in returned_chunk_ids
            if chunk_id in benchmark_case.expected_chunk_ids
        )
        section_hits = sum(
            1
            for section_path in returned_section_paths
            if section_path in benchmark_case.expected_section_paths
        )
        return chunk_hits + section_hits
