from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCaseResult,
    RetrievalBenchmarkReport,
)
from src.application.evaluation.retrieval.benchmarking.reporting.diagnostics import (
    RetrievalBenchmarkFailureDiagnosticBuilder,
)
from src.application.evaluation.retrieval.benchmarking.reporting.summaries import (
    RetrievalBenchmarkReportSummaryBuilder,
)


class RetrievalBenchmarkReportMarkdownRenderer:
    def __init__(
        self,
        *,
        summary_builder: RetrievalBenchmarkReportSummaryBuilder | None = None,
        failure_diagnostic_builder: (
            RetrievalBenchmarkFailureDiagnosticBuilder | None
        ) = None,
        top_chunk_limit: int = 5,
    ) -> None:
        self.summary_builder = (
            summary_builder or RetrievalBenchmarkReportSummaryBuilder()
        )
        self.failure_diagnostic_builder = (
            failure_diagnostic_builder
            or RetrievalBenchmarkFailureDiagnosticBuilder()
        )
        self.top_chunk_limit = top_chunk_limit

    def render(
        self,
        report: RetrievalBenchmarkReport,
    ) -> str:
        lines: list[str] = [
            "# Retrieval Benchmark Report",
            "",
            "## Summary",
        ]
        lines.extend(self._summary_lines(report))
        lines.extend(
            self._breakdown_lines(
                heading="## Breakdown by Document Family",
                rows=self.summary_builder.build_document_family_breakdown(report),
            )
        )
        lines.extend(
            self._breakdown_lines(
                heading="## Breakdown by Query Type",
                rows=self.summary_builder.build_query_type_breakdown(report),
            )
        )
        lines.extend(self._failure_lines(report))
        return "\n".join(lines).strip() + "\n"

    def _summary_lines(
        self,
        report: RetrievalBenchmarkReport,
    ) -> list[str]:
        summary = self.summary_builder.build_overview(report)
        return [
            f"- cases: `{summary['case_count']}`",
            f"- anchor hit rate: `{summary['hit_rate']:.3f}`",
            f"- context hit rate: `{summary['context_hit_rate']:.3f}`",
            f"- MRR: `{summary['mean_reciprocal_rank']:.3f}`",
            f"- recall@1 / @3 / @5 / @10: `{summary['recall_at_1']:.3f}` / `{summary['recall_at_3']:.3f}` / `{summary['recall_at_5']:.3f}` / `{summary['recall_at_10']:.3f}`",
            f"- identifier top-1 accuracy: `{summary['identifier_top_1_accuracy']:.3f}`",
            f"- section-path accuracy: `{summary['section_path_accuracy']:.3f}`",
            f"- evidence completeness: `{summary['evidence_completeness_rate']:.3f}`",
            f"- rank-target satisfaction: `{summary['rank_target_satisfaction_rate']:.3f}`",
            "",
        ]

    def _breakdown_lines(
        self,
        *,
        heading: str,
        rows: list[dict[str, float | int | str]],
    ) -> list[str]:
        lines = [
            heading,
            "",
            "| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for row in rows:
            lines.append(
                "| "
                f"{row['label']} | {row['case_count']} | "
                f"{row['hit_rate']:.3f} | {row['context_hit_rate']:.3f} | "
                f"{row['recall_at_3']:.3f} | {row['mean_reciprocal_rank']:.3f} | "
                f"{row['rank_target_satisfaction_rate']:.3f} |"
            )
        lines.append("")
        return lines

    def _failure_lines(
        self,
        report: RetrievalBenchmarkReport,
    ) -> list[str]:
        failed_results = [
            case_result
            for case_result in report.case_results
            if not case_result.meets_expected_rank_target or not case_result.hit
        ]
        lines = ["## Failure Diagnostics", ""]

        if not failed_results:
            lines.extend(
                [
                    "- no failing benchmark cases",
                    "",
                ]
            )
            return lines

        for case_result in failed_results:
            lines.extend(self._case_failure_lines(case_result))

        return lines

    def _case_failure_lines(
        self,
        case_result: RetrievalBenchmarkCaseResult,
    ) -> list[str]:
        case = case_result.case
        lines = [
            f"### `{case.case_id}` {case.query_text or ''}".rstrip(),
            "",
            f"- query type: `{case.query_type.value if case.query_type is not None else 'unknown'}`",
            f"- expected document: `{case.expected_document_alias or 'unknown'}`",
            f"- expected file: `{case.expected_file_name or 'unknown'}`",
            f"- expected section path: `{case.expected_section_path_text or 'unknown'}`",
            f"- expected page: `{case.expected_page if case.expected_page is not None else 'unknown'}`",
            f"- expected rank target: `{case.expected_rank_target.value if case.expected_rank_target is not None else 'none'}`",
            f"- anchor matched rank: `{case_result.matched_rank if case_result.matched_rank is not None else 'miss'}`",
            f"- context matched rank: `{case_result.context_matched_rank if case_result.context_matched_rank is not None else 'miss'}`",
            f"- expected passage: `{self._single_line(case.expected_relevant_passage)}`",
            "- failure reasons:",
        ]
        for reason in self.failure_diagnostic_builder.build_failure_reasons(case_result):
            lines.append(f"  - {reason}")
        lines.extend(
            self._chunk_table_lines(
                heading="#### Anchor Top Chunks",
                chunks=case_result.returned_chunks,
            )
        )
        lines.extend(
            self._chunk_table_lines(
                heading="#### Context Top Chunks",
                chunks=case_result.context_chunks,
            )
        )
        return lines

    def _chunk_table_lines(
        self,
        *,
        heading: str,
        chunks,
    ) -> list[str]:
        lines = [
            "",
            heading,
            "",
            "| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |",
            "|---|---|---|---|---:|---|---|---|",
        ]
        for index, chunk in enumerate(chunks[: self.top_chunk_limit], start=1):
            pages = self._format_pages(chunk.page_start, chunk.page_end)
            lines.append(
                "| "
                f"{index} | {chunk.chunk_id} | {chunk.document_id} | "
                f"{chunk.retrieval_source} | {chunk.score:.3f} | {pages} | "
                f"{chunk.section_path_text or '-'} | {self._single_line(chunk.content_preview)} |"
            )
        if not chunks:
            lines.append("| - | - | - | - | - | - | - | no chunks returned |")
        lines.append("")
        return lines

    @staticmethod
    def _format_pages(
        page_start: int | None,
        page_end: int | None,
    ) -> str:
        if page_start is None and page_end is None:
            return "-"
        if page_start == page_end or page_end is None:
            return str(page_start)
        if page_start is None:
            return str(page_end)
        return f"{page_start}-{page_end}"

    @staticmethod
    def _single_line(value: str | None) -> str:
        if not value:
            return "-"
        return " ".join(value.split())
