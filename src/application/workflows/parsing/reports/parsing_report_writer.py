from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.config.paths import PROJECT_ROOT

if TYPE_CHECKING:
    from src.application.workflows.parsing.parsing_workflow_result import (
        ParsingWorkflowResult,
    )

_DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "debug_parsing"


class ParsingReportWriter:
    """Writes a JSON parse summary to outputs/debug_parsing/."""

    def __init__(self, output_dir: Path | str | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR

    def write(self, result: ParsingWorkflowResult) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{result.document_id}_parse_report.json"
        ocr_trace = getattr(result, "ocr_trace", None)
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
            "ocr": self._serialize_ocr_trace(ocr_trace),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _serialize_ocr_trace(ocr_trace) -> dict[str, object] | None:
        if ocr_trace is None or type(ocr_trace).__name__ in {"MagicMock", "Mock"}:
            return None

        analyzed_pages = getattr(ocr_trace, "analyzed_pages", None)
        selected_targets = getattr(ocr_trace, "selected_targets", None)
        execution_results = getattr(ocr_trace, "execution_results", None)
        warnings = getattr(ocr_trace, "warnings", None)
        if not isinstance(analyzed_pages, list):
            return None
        if not isinstance(selected_targets, list):
            return None
        if not isinstance(execution_results, list):
            return None
        if warnings is None:
            warnings = []

        return {
            "text_poor_pages": [
                analysis.page_number
                for analysis in analyzed_pages
                if getattr(analysis, "is_text_poor", False)
            ],
            "selected_target_count": len(selected_targets),
            "execution_count": len(execution_results),
            "added_synthetic_elements": getattr(
                ocr_trace,
                "added_synthetic_elements",
                0,
            ),
            "updated_asset_elements": getattr(
                ocr_trace,
                "updated_asset_elements",
                0,
            ),
            "warnings": list(warnings),
            "trace_path": getattr(ocr_trace, "trace_path", None),
        }
