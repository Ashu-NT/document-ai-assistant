from pathlib import Path
from typing import Any

from src.application.reporting.retrieval_benchmark.renderers.markdown_table_helpers import (
    format_float,
    format_pages,
    single_line,
    stringify,
)


class RetrievalBenchmarkResolutionFailureMarkdownRenderer:
    def render(
        self,
        *,
        details: dict[str, Any] | None,
        subset: str,
        truth_set_path: Path | str,
        manifest_path: Path | str,
    ) -> str:
        diagnostics = list((details or {}).get("diagnostics") or [])
        unresolved_case_ids = self._unresolved_case_ids(details)
        lines = [
            "# Retrieval Benchmark Resolution Failure",
            "",
            "## Summary",
            f"- status: `resolution_failed`",
            f"- subset: `{subset}`",
            f"- truth set path: `{truth_set_path}`",
            f"- manifest path: `{manifest_path}`",
            f"- unresolved case count: `{len(unresolved_case_ids)}`",
            (
                "- unresolved case ids: "
                f"`{', '.join(unresolved_case_ids) if unresolved_case_ids else 'none'}`"
            ),
            "",
            "## Diagnostics",
            "",
        ]

        if not diagnostics:
            lines.extend(
                [
                    "- no structured diagnostics were provided",
                    "",
                ]
            )
            return "\n".join(lines).strip() + "\n"

        for diagnostic in diagnostics:
            case_id = diagnostic.get("case_id") or "unknown"
            lines.extend(
                [
                    f"### `{case_id}`",
                    "",
                    f"- document alias: `{diagnostic.get('document_alias') or 'unknown'}`",
                    f"- file name: `{diagnostic.get('file_name') or 'unknown'}`",
                    f"- message: `{single_line(diagnostic.get('message'))}`",
                ]
            )
            details_mapping = diagnostic.get("details") or {}
            if details_mapping:
                lines.append("- details:")
                for key, value in details_mapping.items():
                    lines.append(
                        f"  - `{key}`: `{single_line(stringify(value))}`"
                    )

            candidate_summaries = list(diagnostic.get("candidate_summaries") or [])
            lines.extend(
                [
                    "",
                    "#### Candidate Summaries",
                    "",
                    "| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |",
                    "|---|---|---:|---:|---|---|---|",
                ]
            )
            if not candidate_summaries:
                lines.append("| - | - | - | - | - | - | no candidates |")
            else:
                for index, candidate in enumerate(candidate_summaries, start=1):
                    pages = format_pages(
                        candidate.get("page_start"),
                        candidate.get("page_end"),
                    )
                    lines.append(
                        "| "
                        f"{index} | {candidate.get('chunk_id') or '-'} | "
                        f"{format_float(candidate.get('score'))} | "
                        f"{format_float(candidate.get('passage_overlap'))} | "
                        f"{pages} | "
                        f"{single_line(candidate.get('section_path_text'))} | "
                        f"{single_line(candidate.get('content_preview'))} |"
                    )
            lines.append("")

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def _unresolved_case_ids(details: dict[str, Any] | None) -> list[str]:
        return list((details or {}).get("unresolved_case_ids") or [])
