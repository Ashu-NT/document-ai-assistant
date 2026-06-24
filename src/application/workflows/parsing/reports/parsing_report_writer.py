from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.workflows.parsing.parsing_workflow_result import (
        ParsingWorkflowResult,
    )

_DEFAULT_OUTPUT_DIR = Path("outputs/debug_parsing")


class ParsingReportWriter:
    """Writes a JSON parse summary to outputs/debug_parsing/."""

    def __init__(self, output_dir: Path | str | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR

    def write(self, result: ParsingWorkflowResult) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{result.document_id}_parse_report.json"
        payload = {
            "document_id": result.document_id,
            "file_path": result.file_path,
            "page_count": result.page_count,
            "element_count": result.element_count,
            "section_count": result.section_count,
            "chunk_count": result.chunk_count,
            "table_count": result.table_count,
            "picture_count": result.picture_count,
            "parse_confidence": result.parse_confidence,
            "orphan_element_count": result.orphan_element_count,
            "elements_without_page_count": result.elements_without_page_count,
            "parse_warnings": list(result.parse_warnings),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
