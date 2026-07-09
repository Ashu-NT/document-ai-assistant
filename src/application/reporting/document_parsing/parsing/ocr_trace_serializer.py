from __future__ import annotations


class OcrTraceSerializer:
    """Serializes an OCR trace object into a plain, report-safe dict.

    Defensively duck-typed since callers (including tests) sometimes pass a
    Mock/partial trace object.
    """

    def serialize(self, ocr_trace) -> dict[str, object] | None:
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
