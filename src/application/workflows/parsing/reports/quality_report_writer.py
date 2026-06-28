from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.application.validation.document_quality import DocumentQualityGate
from src.config.paths import PROJECT_ROOT

if TYPE_CHECKING:
    from src.application.workflows.parsing.parsing_workflow_result import (
        ParsingWorkflowResult,
    )

_DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "debug_parsing"


class QualityReportWriter:
    """Runs quality checks and writes results to outputs/debug_parsing/."""

    def __init__(self, output_dir: Path | str | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR
        self._gate = DocumentQualityGate()

    def write(self, result: ParsingWorkflowResult) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{result.document_id}_quality_report.json"

        sections = list(result.document_graph.sections.values())
        elements = list(result.document_graph.elements.values())
        chunks = list(result.document_graph.chunks.values())

        parse_result = self._gate.check_parsing(
            result.document_id,
            sections=sections,
            elements=elements,
            ocr_trace=result.ocr_trace,
        )
        chunk_result = self._gate.check_chunking(
            result.document_id, chunks=chunks
        )

        def _serialise(qr):
            return {
                "passed": qr.passed,
                "summary": qr.summary(),
                "checks": [
                    {
                        "name": c.check_name,
                        "passed": c.passed,
                        "severity": c.severity,
                        "message": c.message,
                        "details": c.details,
                    }
                    for c in qr.checks
                ],
            }

        payload = {
            "document_id": result.document_id,
            "parsing": _serialise(parse_result),
            "chunking": _serialise(chunk_result),
            "overall_passed": parse_result.passed and chunk_result.passed,
        }
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return path
