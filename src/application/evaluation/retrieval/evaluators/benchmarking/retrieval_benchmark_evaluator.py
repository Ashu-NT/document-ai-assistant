from typing import Callable

from src.application.evaluation.retrieval.benchmarking import (
    RetrievalBenchmarkCase,
    RetrievalBenchmarkCaseResult,
    RetrievalBenchmarkChunkSnapshot,
    RetrievalBenchmarkDataset,
    RetrievalBenchmarkReport,
)
from src.application.evaluation.retrieval.evaluators.benchmarking.workflow_result_adapter import (
    WorkflowResultAdapter,
)
from src.shared.exceptions import SchemaValidationError


class RetrievalBenchmarkEvaluator:
    def __init__(
        self,
        *,
        workflow_result_adapter: WorkflowResultAdapter | None = None,
    ) -> None:
        self.workflow_result_adapter = workflow_result_adapter or WorkflowResultAdapter()

    def evaluate(
        self,
        workflow,
        benchmark_cases: RetrievalBenchmarkDataset | list[RetrievalBenchmarkCase],
        progress_callback: Callable[[str], None] | None = None,
    ) -> RetrievalBenchmarkReport:
        case_results: list[RetrievalBenchmarkCaseResult] = []
        cases = self._benchmark_cases(benchmark_cases)
        total_cases = len(cases)

        for index, benchmark_case in enumerate(cases, start=1):
            if benchmark_case.query is None:
                raise SchemaValidationError(
                    "Retrieval benchmark case is missing a query.",
                    details={"case_id": benchmark_case.case_id},
                )

            self._emit_progress(
                progress_callback,
                (
                    f"[{index}/{total_cases}] Running benchmark case "
                    f"{benchmark_case.case_id}"
                ),
            )
            workflow_result = workflow.run(benchmark_case.query)
            workflow_output = self.workflow_result_adapter.to_workflow_output(
                workflow_result
            )

            anchor_match = self._first_relevant_rank(
                benchmark_case=benchmark_case,
                chunks=workflow_output.anchor_chunks,
            )
            context_match = self._first_relevant_rank(
                benchmark_case=benchmark_case,
                chunks=workflow_output.context_chunks,
            )
            anchor_section_path_hits = self._section_path_hits(
                benchmark_case=benchmark_case,
                chunks=workflow_output.anchor_chunks,
            )
            context_section_path_hits = self._section_path_hits(
                benchmark_case=benchmark_case,
                chunks=workflow_output.context_chunks,
            )
            case_results.append(
                RetrievalBenchmarkCaseResult(
                    case=benchmark_case,
                    returned_chunk_ids=[
                        chunk.chunk_id for chunk in workflow_output.anchor_chunks
                    ],
                    returned_section_paths=[
                        list(chunk.section_path)
                        for chunk in workflow_output.anchor_chunks
                    ],
                    returned_chunks=self._build_chunk_snapshots(
                        workflow_output.anchor_chunks
                    ),
                    context_chunk_ids=[
                        chunk.chunk_id for chunk in workflow_output.context_chunks
                    ],
                    context_section_paths=[
                        list(chunk.section_path)
                        for chunk in workflow_output.context_chunks
                    ],
                    context_chunks=self._build_chunk_snapshots(
                        workflow_output.context_chunks
                    ),
                    hit=anchor_match is not None,
                    reciprocal_rank=self._reciprocal_rank(anchor_match),
                    relevant_hits=self._relevant_hits(
                        benchmark_case=benchmark_case,
                        chunks=workflow_output.anchor_chunks,
                    ),
                    matched_rank=anchor_match,
                    context_hit=context_match is not None,
                    context_reciprocal_rank=self._reciprocal_rank(context_match),
                    context_relevant_hits=self._relevant_hits(
                        benchmark_case=benchmark_case,
                        chunks=workflow_output.context_chunks,
                    ),
                    context_matched_rank=context_match,
                    exact_section_path_hit=bool(anchor_section_path_hits),
                    context_exact_section_path_hit=bool(context_section_path_hits),
                    evidence_completeness=self._evidence_completeness(
                        benchmark_case=benchmark_case,
                        context_chunks=workflow_output.context_chunks,
                        context_section_path_hits=context_section_path_hits,
                    ),
                    used_context_expansion=workflow_output.used_context_expansion,
                )
            )
            self._emit_progress(
                progress_callback,
                (
                    f"[{index}/{total_cases}] Completed {benchmark_case.case_id} "
                    f"(anchor_hit={'yes' if anchor_match is not None else 'no'}, "
                    f"context_hit={'yes' if context_match is not None else 'no'})"
                ),
            )

        return RetrievalBenchmarkReport(case_results=case_results)

    @staticmethod
    def _benchmark_cases(
        benchmark_cases: RetrievalBenchmarkDataset | list[RetrievalBenchmarkCase],
    ) -> list[RetrievalBenchmarkCase]:
        if isinstance(benchmark_cases, RetrievalBenchmarkDataset):
            return list(benchmark_cases.cases)
        return list(benchmark_cases)

    def _first_relevant_rank(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        chunks: list,
    ) -> int | None:
        for index, chunk in enumerate(chunks, start=1):
            if self._is_relevant_chunk(benchmark_case=benchmark_case, chunk=chunk):
                return index

        return None

    def _relevant_hits(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        chunks: list,
    ) -> int:
        return sum(
            1
            for chunk in chunks
            if self._is_relevant_chunk(benchmark_case=benchmark_case, chunk=chunk)
        )

    @staticmethod
    def _reciprocal_rank(rank: int | None) -> float:
        if rank is None:
            return 0.0
        return 1.0 / rank

    def _is_relevant_chunk(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        chunk,
    ) -> bool:
        if chunk.chunk_id in benchmark_case.expected_chunk_ids:
            return True

        section_path = list(getattr(chunk, "section_path", []))
        return section_path in benchmark_case.expected_section_paths

    def _section_path_hits(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        chunks: list,
    ) -> list[list[str]]:
        return [
            list(chunk.section_path)
            for chunk in chunks
            if list(chunk.section_path) in benchmark_case.expected_section_paths
        ]

    def _evidence_completeness(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        context_chunks: list,
        context_section_path_hits: list[list[str]],
    ) -> float:
        if benchmark_case.expected_chunk_ids:
            matched_chunk_ids = {
                chunk.chunk_id
                for chunk in context_chunks
                if chunk.chunk_id in benchmark_case.expected_chunk_ids
            }
            return len(matched_chunk_ids) / len(benchmark_case.expected_chunk_ids)

        if benchmark_case.expected_section_paths:
            return 1.0 if context_section_path_hits else 0.0

        return 0.0

    def _build_chunk_snapshots(
        self,
        chunks: list,
    ) -> list[RetrievalBenchmarkChunkSnapshot]:
        return [
            RetrievalBenchmarkChunkSnapshot(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                retrieval_source=getattr(chunk, "retrieval_source", "unknown"),
                score=getattr(chunk, "score", 0.0),
                chunk_type=self._chunk_type_value(getattr(chunk, "chunk_type", "")),
                section_id=getattr(chunk, "section_id", None),
                section_path=list(getattr(chunk, "section_path", [])),
                page_start=getattr(getattr(chunk, "source", None), "page_start", None),
                page_end=getattr(getattr(chunk, "source", None), "page_end", None),
                content_preview=self._content_preview(getattr(chunk, "content", "")),
            )
            for chunk in chunks
        ]

    @staticmethod
    def _chunk_type_value(chunk_type) -> str:
        return getattr(chunk_type, "value", str(chunk_type) or "unknown")

    @staticmethod
    def _content_preview(
        content: str,
        max_length: int = 180,
    ) -> str:
        normalized = " ".join((content or "").split())
        if len(normalized) <= max_length:
            return normalized
        return normalized[: max_length - 3].rstrip() + "..."

    @staticmethod
    def _emit_progress(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)
