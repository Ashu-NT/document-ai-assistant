from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    invalid_request_result,
)
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class BenchmarkStatisticsRequest(ToolRequest):
    report_path: str | None = None
    report_data: dict[str, Any] | None = None


class BenchmarkStatisticsTool:
    metadata = ToolMetadata(
        tool_name="benchmark_statistics",
        category="evaluation",
        description="Read benchmark report statistics without rerunning the benchmark.",
        mutates_state=False,
    )

    def run(self, request: BenchmarkStatisticsRequest) -> ToolResult:
        if request.report_data is None and not request.report_path:
            return invalid_request_result(
                "Provide report_path or report_data.",
                metadata=self.metadata,
            )

        try:
            report_data = request.report_data or self._load_report(request.report_path)
        except ApplicationError as exc:
            return ToolResult.fail(
                exc.message,
                error_code=exc.error_code,
                diagnostics=exc.details,
                metadata=self.metadata,
            )
        summary = dict(report_data.get("summary") or {})
        return ToolResult.ok(
            data={
                "summary": summary,
                "document_family_breakdown": (
                    report_data.get("document_family_breakdown") or {}
                ),
                "query_type_breakdown": report_data.get("query_type_breakdown") or {},
                "case_count": len(report_data.get("case_results") or []),
            },
            metadata=self.metadata,
        )

    @staticmethod
    def _load_report(report_path: str | None) -> dict[str, Any]:
        path = Path(report_path or "")
        if not path.exists():
            raise ApplicationError(
                "Benchmark report file was not found.",
                error_code="benchmark_failed",
                details={"report_path": str(path)},
            )
        return json.loads(path.read_text(encoding="utf-8"))
