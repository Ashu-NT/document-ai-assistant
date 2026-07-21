from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from src.application.workflows.parsing.ocr.ocr_target import OCRTarget
from src.application.workflows.parsing.ocr.ocr_target_execution_result import (
    OCRTargetExecutionResult,
)
from src.application.workflows.parsing.ocr.page_text_quality import PageTextQuality
from src.config.paths import ensure_directory


@dataclass(slots=True)
class OCRTrace:
    document_path: str
    page_count: int
    analyzed_pages: list[PageTextQuality] = field(default_factory=list)
    selected_targets: list[OCRTarget] = field(default_factory=list)
    execution_results: list[OCRTargetExecutionResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    added_synthetic_elements: int = 0
    updated_asset_elements: int = 0
    trace_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "document_path": self.document_path,
            "page_count": self.page_count,
            "text_poor_pages": [
                analysis.page_number
                for analysis in self.analyzed_pages
                if analysis.is_text_poor
            ],
            "analyzed_pages": [
                {
                    "page_number": analysis.page_number,
                    "text_char_count": analysis.text_char_count,
                    "word_count": analysis.word_count,
                    "element_count": analysis.element_count,
                    "table_count": analysis.table_count,
                    "image_count": analysis.image_count,
                    "text_density": analysis.text_density,
                    "image_area_ratio": analysis.image_area_ratio,
                    "has_text": analysis.has_text,
                    "is_text_poor": analysis.is_text_poor,
                    "is_probably_scanned": analysis.is_probably_scanned,
                    "reasons": list(analysis.reasons),
                }
                for analysis in self.analyzed_pages
            ],
            "selected_targets": [
                {
                    "target_id": target.target_id,
                    "target_type": target.target_type.value,
                    "page_number": target.page_number,
                    "source_element_id": target.source_element_id,
                    "reason": target.reason,
                    "priority": target.priority,
                    "image_path": target.image_path,
                    "bbox": (
                        None
                        if target.bbox is None
                        else {
                            "x1": target.bbox.x1,
                            "y1": target.bbox.y1,
                            "x2": target.bbox.x2,
                            "y2": target.bbox.y2,
                        }
                    ),
                    "metadata": dict(target.metadata),
                }
                for target in self.selected_targets
            ],
            "execution_results": [
                {
                    "target_id": execution.target.target_id,
                    "target_type": execution.target.target_type.value,
                    "page_number": execution.target.page_number,
                    "source_image_path": execution.source_image_path,
                    "succeeded": execution.succeeded,
                    "text_length": len(execution.ocr_result.text.strip())
                    if execution.ocr_result is not None
                    else 0,
                    "confidence": (
                        execution.ocr_result.confidence
                        if execution.ocr_result is not None
                        else None
                    ),
                    "provider_name": (
                        execution.ocr_result.provider_name
                        if execution.ocr_result is not None
                        else None
                    ),
                    "error": execution.error,
                }
                for execution in self.execution_results
            ],
            "warnings": list(self.warnings),
            "added_synthetic_elements": self.added_synthetic_elements,
            "updated_asset_elements": self.updated_asset_elements,
        }

    def write(self, output_dir: Path, document_id: str) -> Path:
        ensure_directory(output_dir)
        output_path = output_dir / f"{document_id}_ocr_trace.json"
        output_path.write_text(
            json.dumps(self.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        self.trace_path = str(output_path)
        return output_path

