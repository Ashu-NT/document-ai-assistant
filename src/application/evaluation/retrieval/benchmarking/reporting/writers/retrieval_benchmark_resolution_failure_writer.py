import json
from pathlib import Path
from typing import Any


class RetrievalBenchmarkResolutionFailureWriter:
    def write_json(
        self,
        *,
        details: dict[str, Any] | None,
        output_path: Path | str,
        subset: str,
        truth_set_path: Path | str,
        manifest_path: Path | str,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            json.dumps(
                self._build_payload(
                    details=details,
                    subset=subset,
                    truth_set_path=truth_set_path,
                    manifest_path=manifest_path,
                ),
                indent=2,
            ),
            encoding="utf-8",
        )
        return resolved_path

    def write_markdown(
        self,
        *,
        details: dict[str, Any] | None,
        output_path: Path | str,
        subset: str,
        truth_set_path: Path | str,
        manifest_path: Path | str,
    ) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(
            self._render_markdown(
                details=details,
                subset=subset,
                truth_set_path=truth_set_path,
                manifest_path=manifest_path,
            ),
            encoding="utf-8",
        )
        return resolved_path

    def _build_payload(
        self,
        *,
        details: dict[str, Any] | None,
        subset: str,
        truth_set_path: Path | str,
        manifest_path: Path | str,
    ) -> dict[str, Any]:
        unresolved_case_ids = self._unresolved_case_ids(details)
        return {
            "status": "resolution_failed",
            "subset": subset,
            "truth_set_path": str(truth_set_path),
            "manifest_path": str(manifest_path),
            "unresolved_case_count": len(unresolved_case_ids),
            "unresolved_case_ids": unresolved_case_ids,
            "diagnostics": list((details or {}).get("diagnostics") or []),
        }

    def _render_markdown(
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
                    f"- message: `{self._single_line(diagnostic.get('message'))}`",
                ]
            )
            details_mapping = diagnostic.get("details") or {}
            if details_mapping:
                lines.append("- details:")
                for key, value in details_mapping.items():
                    lines.append(
                        f"  - `{key}`: `{self._single_line(self._stringify(value))}`"
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
                    pages = self._format_pages(
                        candidate.get("page_start"),
                        candidate.get("page_end"),
                    )
                    lines.append(
                        "| "
                        f"{index} | {candidate.get('chunk_id') or '-'} | "
                        f"{self._format_float(candidate.get('score'))} | "
                        f"{self._format_float(candidate.get('passage_overlap'))} | "
                        f"{pages} | "
                        f"{self._single_line(candidate.get('section_path_text'))} | "
                        f"{self._single_line(candidate.get('content_preview'))} |"
                    )
            lines.append("")

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def _unresolved_case_ids(details: dict[str, Any] | None) -> list[str]:
        return list((details or {}).get("unresolved_case_ids") or [])

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
    def _format_float(value: Any) -> str:
        if isinstance(value, int | float):
            return f"{float(value):.3f}"
        return "-"

    @staticmethod
    def _stringify(value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    @staticmethod
    def _single_line(value: Any) -> str:
        if value is None:
            return "-"
        return " ".join(str(value).split())
