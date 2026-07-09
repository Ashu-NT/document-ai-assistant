from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.application.reporting.document_parsing.parsing.parsing_report_builder import (
    ParsingReportBuilder,
)
from src.config.paths import PROJECT_ROOT

if TYPE_CHECKING:
    from src.application.workflows.parsing.parsing_workflow_result import (
        ParsingWorkflowResult,
    )

_DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "debug_parsing"


class ParsingReportWriter:
    """Writes a JSON parse summary to outputs/debug_parsing/."""

    def __init__(
        self,
        output_dir: Path | str | None = None,
        *,
        report_builder: ParsingReportBuilder | None = None,
    ) -> None:
        self.output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR
        self.report_builder = report_builder or ParsingReportBuilder()

    def write(self, result: ParsingWorkflowResult) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{result.document_id}_parse_report.json"
        payload = self.report_builder.build(result)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
