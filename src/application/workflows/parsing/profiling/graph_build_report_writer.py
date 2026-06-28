from __future__ import annotations

import json
from pathlib import Path


class GraphBuildReportWriter:
    def __init__(self, output_dir: Path | str) -> None:
        self.output_dir = Path(output_dir)

    def write(
        self,
        *,
        report_data: dict[str, object],
    ) -> tuple[Path, Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "graph_build_report.json"
        markdown_path = self.output_dir / "performance_report.md"
        json_path.write_text(
            json.dumps(report_data, indent=2),
            encoding="utf-8",
        )
        markdown_path.write_text(
            self._to_markdown(report_data),
            encoding="utf-8",
        )
        return json_path, markdown_path

    def _to_markdown(self, report_data: dict[str, object]) -> str:
        input_document = report_data["input_document"]
        counts = report_data["counts"]
        timings = report_data["timings"]
        stage_metrics = report_data["stage_metrics"]
        cprofile = report_data["cprofile"]
        memory = report_data["memory"]
        architecture_map = report_data["architecture_map"]
        bottlenecks = report_data["ranked_bottlenecks"]
        operation_profiles = report_data.get("operation_profiles") or {}

        lines = [
            "# Parsing Pipeline Performance Report",
            "",
            "## Input Document",
            f"- File: `{input_document['file_path']}`",
            f"- Pages: `{input_document['page_count']}`",
            "",
            "## Output Counts",
            f"- Canonical elements: `{counts['canonical_elements']}`",
            f"- Sections: `{counts['sections']}`",
            f"- Elements: `{counts['elements']}`",
            f"- Chunks: `{counts['chunks']}`",
            f"- Tables: `{counts['tables']}`",
            f"- Pictures: `{counts['pictures']}`",
            "",
            "## Timings",
            f"- Docling conversion: `{self._resolve_timing(timings, 'docling_conversion_seconds', 'raw_parse_seconds'):.3f}s`",
            f"- Canonical normalization: `{self._resolve_timing(timings, 'canonical_normalization_seconds', 'normalize_seconds'):.3f}s`",
            f"- Graph build: `{timings['graph_build_seconds']:.3f}s`",
        ]
        profiled = timings.get("profiled_graph_build_seconds")
        if isinstance(profiled, (int, float)):
            lines.append(f"- Profiled graph build: `{profiled:.3f}s`")
        baseline = timings.get("baseline_graph_build_seconds")
        if isinstance(baseline, (int, float)) and baseline > 0:
            improvement = timings.get("graph_build_improvement_percent")
            lines.append(f"- Baseline graph build: `{baseline:.3f}s`")
            if isinstance(improvement, (int, float)):
                lines.append(f"- Improvement: `{improvement:.2f}%`")
        if isinstance(operation_profiles, dict) and operation_profiles:
            lines.extend(
                [
                    "",
                    "## Operation Profiles",
                    "| Operation | Elapsed | Peak Memory | cProfile Dump |",
                    "| --- | ---: | ---: | --- |",
                ]
            )
            for key, profile in operation_profiles.items():
                if not isinstance(profile, dict):
                    continue
                memory_profile = profile.get("memory", {})
                cprofile_profile = profile.get("cprofile", {})
                elapsed_seconds = float(profile.get("elapsed_seconds", 0.0))
                peak_bytes = memory_profile.get("peak_bytes", 0)
                prof_path = cprofile_profile.get("prof_path", "")
                lines.append(
                    "| "
                    f"{self._display_operation_name(key)} | "
                    f"{elapsed_seconds:.3f}s | "
                    f"{peak_bytes} | "
                    f"`{prof_path}` |"
                )
        lines.extend(
            [
                "",
                "## Stage Metrics",
                "| Stage | Start | End | Elapsed | Inputs | Outputs | Operations |",
                "| --- | ---: | ---: | ---: | --- | --- | --- |",
            ]
        )
        for metric in stage_metrics:
            lines.append(
                "| "
                f"{metric['name']} | "
                f"{metric['started_at_offset_seconds']:.3f}s | "
                f"{metric['ended_at_offset_seconds']:.3f}s | "
                f"{metric['elapsed_seconds']:.3f}s | "
                f"{self._format_mapping(metric['input_counts'])} | "
                f"{self._format_mapping(metric['output_counts'])} | "
                f"{self._format_mapping(metric['operations'])} |"
            )

        lines.extend(
            [
                "",
                "## Architecture Map",
                "| Stage | Class | Function | Complexity | Responsibility | Why |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for descriptor in architecture_map:
            lines.append(
                "| "
                f"{descriptor['name']} | "
                f"{descriptor['owner']} | "
                f"{descriptor['function']} | "
                f"{descriptor['worst_case_complexity']} | "
                f"{descriptor['responsibility']} | "
                f"{descriptor['complexity_reason']} |"
            )

        lines.extend(
            [
                "",
                "## Ranked Bottlenecks",
                "| Rank | Function | Complexity | Runtime % | Evidence | Recommendation |",
                "| ---: | --- | --- | ---: | --- | --- |",
            ]
        )
        for bottleneck in bottlenecks:
            lines.append(
                "| "
                f"{bottleneck['rank']} | "
                f"{bottleneck['function']} | "
                f"{bottleneck['complexity']} | "
                f"{bottleneck['runtime_percent']:.2f}% | "
                f"{bottleneck['evidence']} | "
                f"{bottleneck['recommendation']} |"
            )

        lines.extend(
            [
                "",
                "## cProfile Top Cumulative",
                "| Calls | Function | Cumulative (s) | Total (s) |",
                "| ---: | --- | ---: | ---: |",
            ]
        )
        for entry in cprofile["top_cumulative"]:
            lines.append(
                "| "
                f"{entry['calls']} | "
                f"{entry['function']} | "
                f"{entry['cumulative_seconds']:.6f} | "
                f"{entry['total_seconds']:.6f} |"
            )

        lines.extend(
            [
                "",
                "## cProfile Top Call Count",
                "| Calls | Function | Cumulative (s) | Total (s) |",
                "| ---: | --- | ---: | ---: |",
            ]
        )
        for entry in cprofile["top_call_count"]:
            lines.append(
                "| "
                f"{entry['calls']} | "
                f"{entry['function']} | "
                f"{entry['cumulative_seconds']:.6f} | "
                f"{entry['total_seconds']:.6f} |"
            )

        if isinstance(operation_profiles, dict) and operation_profiles:
            lines.extend(
                [
                    "",
                    "## Operation cProfile Highlights",
                ]
            )
            for key, profile in operation_profiles.items():
                if not isinstance(profile, dict):
                    continue
                cprofile_profile = profile.get("cprofile", {})
                top_cumulative = cprofile_profile.get("top_cumulative", [])
                if not top_cumulative:
                    continue
                lines.extend(
                    [
                        "",
                        f"### {self._display_operation_name(key)}",
                        "| Calls | Function | Cumulative (s) | Total (s) |",
                        "| ---: | --- | ---: | ---: |",
                    ]
                )
                for entry in top_cumulative[:10]:
                    lines.append(
                        "| "
                        f"{entry['calls']} | "
                        f"{entry['function']} | "
                        f"{entry['cumulative_seconds']:.6f} | "
                        f"{entry['total_seconds']:.6f} |"
                    )

        lines.extend(
            [
                "",
                "## Memory",
                f"- Peak traced memory: `{memory['peak_bytes']}` bytes",
                f"- Current traced memory: `{memory['current_bytes']}` bytes",
                "",
                "### Top Allocation Sites",
            ]
        )
        for stat in memory["top_allocations"]:
            lines.append(
                f"- `{stat['trace']}` -> `{stat['size_bytes']}` bytes across `{stat['count']}` block(s)"
            )

        return "\n".join(lines) + "\n"

    @staticmethod
    def _format_mapping(value: object) -> str:
        if not isinstance(value, dict) or not value:
            return "-"
        return ", ".join(
            f"{key}={mapped_value}"
            for key, mapped_value in value.items()
        )

    @staticmethod
    def _resolve_timing(
        timings: dict[str, object],
        primary_key: str,
        fallback_key: str,
    ) -> float:
        value = timings.get(primary_key, timings.get(fallback_key, 0.0))
        return float(value) if isinstance(value, (int, float)) else 0.0

    @staticmethod
    def _display_operation_name(value: object) -> str:
        operation_names = {
            "docling_conversion": "Docling Conversion",
            "canonical_normalization": "Canonical Normalization",
            "graph_build": "Document Graph Build",
        }
        return operation_names.get(str(value), str(value).replace("_", " ").title())
