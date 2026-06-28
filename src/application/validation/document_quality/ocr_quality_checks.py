from __future__ import annotations

from src.application.validation.document_quality.quality_check_result import (
    QualityCheckResult,
)


def check_ocr_target_failures(ocr_trace) -> QualityCheckResult:
    name = "parser.ocr_target_failures"
    if ocr_trace is None or not ocr_trace.selected_targets:
        return QualityCheckResult.ok(name)

    failure_count = sum(
        1 for execution in ocr_trace.execution_results if not execution.succeeded
    )
    if failure_count == 0:
        return QualityCheckResult.ok(name)

    return QualityCheckResult.warn(
        name,
        f"{failure_count} OCR target(s) failed during parsing fallback.",
        details={
            "selected_target_count": len(ocr_trace.selected_targets),
            "failure_count": failure_count,
        },
    )


def check_ocr_targets_have_page_numbers(ocr_trace) -> QualityCheckResult:
    name = "parser.ocr_targets_have_pages"
    if ocr_trace is None:
        return QualityCheckResult.ok(name)

    missing_pages = [
        execution.target.target_id
        for execution in ocr_trace.execution_results
        if execution.target.page_number is None
    ]
    if missing_pages:
        return QualityCheckResult.warn(
            name,
            "Some OCR targets completed without a page number.",
            details={"target_ids": missing_pages},
        )
    return QualityCheckResult.ok(name)
