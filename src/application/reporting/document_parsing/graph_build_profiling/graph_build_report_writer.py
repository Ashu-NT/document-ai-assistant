from __future__ import annotations

import json
from pathlib import Path

from src.application.reporting.document_parsing.graph_build_profiling.graph_build_report_markdown_renderer import (
    GraphBuildReportMarkdownRenderer,
)


class GraphBuildReportWriter:
    def __init__(
        self,
        output_dir: Path | str,
        *,
        markdown_renderer: GraphBuildReportMarkdownRenderer | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.markdown_renderer = markdown_renderer or GraphBuildReportMarkdownRenderer()

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
            self.markdown_renderer.render(report_data),
            encoding="utf-8",
        )
        return json_path, markdown_path
