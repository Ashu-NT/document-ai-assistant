from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.application.evaluation.retrieval import RetrievalQualityGate
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class RunQualityGateRequest(ToolRequest):
    report_path: str | None = None
    report_data: dict[str, Any] | None = None
    thresholds_path: str | None = None


class RunQualityGateTool:
    metadata = ToolMetadata(
        tool_name="run_quality_gate",
        category="evaluation",
        description="Check a retrieval benchmark report against threshold configuration.",
        mutates_state=False,
    )

    def run(self, request: RunQualityGateRequest) -> ToolResult:
        if request.report_data is None and not request.report_path:
            return invalid_request_result(
                "Provide report_path or report_data.",
                metadata=self.metadata,
            )

        try:
            report_data = request.report_data or self._load_report(request.report_path)
            result = RetrievalQualityGate(
                thresholds_path=request.thresholds_path
            ).check(report_data)
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        payload = {
            "passed": result.passed,
            "violations": [
                {
                    "metric": violation.metric,
                    "actual": violation.actual,
                    "threshold": violation.threshold,
                    "message": violation.message,
                }
                for violation in result.violations
            ],
            "checked_metrics": result.checked_metrics,
            "summary": result.summary(),
        }
        if result.passed:
            return ToolResult.ok(data=payload, metadata=self.metadata)

        return ToolResult.fail(
            result.summary(),
            error_code="quality_gate_failed",
            diagnostics=payload,
            metadata=self.metadata,
            data=payload,
        )

    @staticmethod
    def _load_report(report_path: str | None) -> dict[str, Any]:
        if not report_path:
            raise ApplicationError(
                "report_path is required when report_data is not provided.",
                error_code="invalid_request",
            )
        path = Path(report_path)
        if not path.exists():
            raise ApplicationError(
                "Benchmark report file was not found.",
                error_code="benchmark_failed",
                details={"report_path": str(path)},
            )
        return json.loads(path.read_text(encoding="utf-8"))
