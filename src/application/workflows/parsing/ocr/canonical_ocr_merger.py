from __future__ import annotations

import re

from src.application.contracts.ai import OCRResult
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.ocr.ocr_merge_policy import OCRMergePolicy
from src.application.workflows.parsing.ocr.ocr_merge_result import OCRMergeResult
from src.application.workflows.parsing.ocr.ocr_target_execution_result import (
    OCRTargetExecutionResult,
)
from src.application.workflows.parsing.ocr.ocr_target_type import OCRTargetType
from src.application.workflows.parsing.ocr.ocr_trace import OCRTrace
from src.domain.common import ElementType
from src.shared.ids import IdGenerator, IdPrefix


class CanonicalOCRMerger:
    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        merge_policy: OCRMergePolicy,
    ) -> None:
        self.id_generator = id_generator
        self.merge_policy = merge_policy

    def merge(
        self,
        *,
        document_path: str,
        page_count: int,
        canonical_elements: list[CanonicalElement],
        selection_result,
        execution_results: list[OCRTargetExecutionResult],
        persist_trace: bool = False,
        trace_output_dir=None,
        document_id: str | None = None,
    ) -> OCRMergeResult:
        merged_elements = list(canonical_elements)
        warnings = list(selection_result.warnings)
        added_synthetic_elements = 0
        updated_asset_elements = 0

        for execution in execution_results:
            if execution.target.target_type == OCRTargetType.ASSET:
                if self._merge_asset_target(merged_elements, execution):
                    updated_asset_elements += 1
                if execution.error:
                    warnings.append(
                        f"Asset OCR failed for {execution.target.target_id}: {execution.error}"
                    )
                continue

            if execution.error:
                warnings.append(
                    f"OCR fallback failed for {execution.target.target_id}: {execution.error}"
                )
                continue
            if execution.ocr_result is None:
                continue
            if not self._should_attach_as_text(execution.ocr_result):
                warnings.append(
                    f"OCR result below confidence threshold for {execution.target.target_id}."
                )
                continue
            if self._is_duplicate_text(merged_elements, execution):
                continue

            synthetic_element = self._build_synthetic_element(
                merged_elements=merged_elements,
                execution=execution,
            )
            insertion_index = self._resolve_insertion_index(
                merged_elements,
                execution,
            )
            merged_elements.insert(insertion_index, synthetic_element)
            added_synthetic_elements += 1

        self._renumber_order_indexes(merged_elements)
        trace = OCRTrace(
            document_path=document_path,
            page_count=page_count,
            analyzed_pages=list(selection_result.page_analyses),
            selected_targets=list(selection_result.targets),
            execution_results=list(execution_results),
            warnings=warnings,
            added_synthetic_elements=added_synthetic_elements,
            updated_asset_elements=updated_asset_elements,
        )
        resolved_document_id = document_id or self._resolve_document_id(merged_elements)
        if persist_trace and trace_output_dir is not None and resolved_document_id:
            trace.write(trace_output_dir, resolved_document_id)

        return OCRMergeResult(
            canonical_elements=merged_elements,
            ocr_trace=trace,
            warnings=warnings,
            added_synthetic_elements=added_synthetic_elements,
            updated_asset_elements=updated_asset_elements,
        )

    def _merge_asset_target(
        self,
        merged_elements: list[CanonicalElement],
        execution: OCRTargetExecutionResult,
    ) -> bool:
        element = self._find_source_element(merged_elements, execution)
        if element is None:
            return False

        if execution.error:
            element.metadata["ocr_error"] = execution.error
            return True

        if execution.ocr_result is None:
            return False

        self._attach_ocr_metadata(
            element=element,
            execution=execution,
            attach_as_main_text=self._should_attach_as_text(execution.ocr_result),
        )
        return True

    def _build_synthetic_element(
        self,
        *,
        merged_elements: list[CanonicalElement],
        execution: OCRTargetExecutionResult,
    ) -> CanonicalElement:
        source_element = self._find_source_element(merged_elements, execution)
        document_id = (
            source_element.document_id
            if source_element is not None
            else self._resolve_document_id(merged_elements)
        )
        section_path = (
            list(source_element.section_path)
            if source_element is not None
            else []
        )
        metadata = self._build_metadata(execution)
        metadata["source"] = f"ocr_{execution.target.target_type.value}_fallback"

        return CanonicalElement(
            element_id=self.id_generator.new_id(IdPrefix.ELEMENT),
            document_id=document_id,
            element_type=ElementType.TEXT,
            text=execution.ocr_result.text.strip() if execution.ocr_result else None,
            page_start=execution.target.page_number,
            page_end=execution.target.page_number,
            bbox=execution.target.bbox,
            order_index=source_element.order_index + 1 if source_element else len(merged_elements) + 1,
            section_title=None,
            section_path=section_path,
            raw_ref=execution.target.target_id,
            metadata=metadata,
        )

    def _resolve_insertion_index(
        self,
        merged_elements: list[CanonicalElement],
        execution: OCRTargetExecutionResult,
    ) -> int:
        source_element = self._find_source_element(merged_elements, execution)
        if source_element is not None:
            for index, element in enumerate(merged_elements):
                if element.element_id == source_element.element_id:
                    return index + 1

        page_number = execution.target.page_number
        if page_number is not None:
            last_page_index = None
            for index, element in enumerate(merged_elements):
                if element.page_start == page_number or element.page_end == page_number:
                    last_page_index = index
            if last_page_index is not None:
                return last_page_index + 1
        return len(merged_elements)

    def _attach_ocr_metadata(
        self,
        *,
        element: CanonicalElement,
        execution: OCRTargetExecutionResult,
        attach_as_main_text: bool,
    ) -> None:
        metadata = element.metadata
        metadata.update(self._build_metadata(execution))
        if execution.ocr_result is None:
            return
        if attach_as_main_text:
            metadata["ocr_text"] = execution.ocr_result.text.strip()
        else:
            metadata["ocr_low_confidence_text"] = execution.ocr_result.text.strip()

    def _build_metadata(
        self,
        execution: OCRTargetExecutionResult,
    ) -> dict[str, object]:
        ocr_result = execution.ocr_result
        return {
            "ocr_text": ocr_result.text.strip() if ocr_result is not None else "",
            "ocr_provider": (
                ocr_result.provider_name if ocr_result is not None else None
            ),
            "ocr_confidence": (
                ocr_result.confidence if ocr_result is not None else None
            ),
            "ocr_target_type": execution.target.target_type.value,
            "ocr_target_id": execution.target.target_id,
            "ocr_reason": execution.target.reason,
            "ocr_source_image_path": execution.source_image_path,
            "ocr_diagnostics": (
                dict(ocr_result.diagnostics) if ocr_result is not None else {}
            ),
        }

    def _should_attach_as_text(self, ocr_result: OCRResult) -> bool:
        if not ocr_result.text.strip():
            return False
        if ocr_result.confidence is None:
            return True
        if ocr_result.confidence >= self.merge_policy.min_confidence:
            return True
        return self.merge_policy.attach_low_confidence_text

    def _is_duplicate_text(
        self,
        merged_elements: list[CanonicalElement],
        execution: OCRTargetExecutionResult,
    ) -> bool:
        if execution.ocr_result is None:
            return True

        candidate = self._normalize_text(execution.ocr_result.text)
        if not candidate:
            return True

        page_number = execution.target.page_number
        existing_page_text = " ".join(
            self._normalize_text(element.text)
            for element in merged_elements
            if page_number is not None
            and element.text
            and (
                element.page_start == page_number
                or element.page_end == page_number
            )
        )
        return len(candidate) >= 24 and candidate in existing_page_text

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if value is None:
            return ""
        return re.sub(r"\s+", " ", value).strip().lower()

    @staticmethod
    def _renumber_order_indexes(elements: list[CanonicalElement]) -> None:
        for index, element in enumerate(elements, start=1):
            element.order_index = index

    @staticmethod
    def _resolve_document_id(elements: list[CanonicalElement]) -> str:
        return elements[0].document_id if elements else ""

    @staticmethod
    def _find_source_element(
        merged_elements: list[CanonicalElement],
        execution: OCRTargetExecutionResult,
    ) -> CanonicalElement | None:
        source_element_id = execution.target.source_element_id
        if source_element_id is None:
            return None
        for element in merged_elements:
            if element.element_id == source_element_id:
                return element
        return None

