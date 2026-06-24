from __future__ import annotations

from typing import TYPE_CHECKING

from src.application.validation.document_quality.quality_check_result import (
    QualityCheckResult,
)

if TYPE_CHECKING:
    from src.domain.document import DocumentSection
    from src.domain.elements import CanonicalElement


_MAX_ORPHAN_RATIO = 0.25
_MIN_SECTIONS_FOR_DOCUMENT = 1


def check_orphan_element_ratio(
    elements: list[CanonicalElement],
    sections: list[DocumentSection],
) -> QualityCheckResult:
    name = "parser.orphan_element_ratio"
    if not elements:
        return QualityCheckResult.ok(name)
    orphans = [e for e in elements if not getattr(e, "section_id", None)]
    ratio = len(orphans) / len(elements)
    if ratio > _MAX_ORPHAN_RATIO:
        return QualityCheckResult.warn(
            name,
            f"High orphan element ratio: {ratio:.1%} ({len(orphans)}/{len(elements)})",
            details={"orphan_count": len(orphans), "total": len(elements), "ratio": ratio},
        )
    return QualityCheckResult.ok(name)


def check_elements_have_pages(
    elements: list[CanonicalElement],
) -> QualityCheckResult:
    name = "parser.elements_without_page"
    if not elements:
        return QualityCheckResult.ok(name)
    missing = [e for e in elements if getattr(e, "page_number", None) is None]
    ratio = len(missing) / len(elements)
    if ratio > 0.5:
        return QualityCheckResult.warn(
            name,
            f"{ratio:.1%} of elements have no page number",
            details={"missing_page_count": len(missing), "total": len(elements)},
        )
    return QualityCheckResult.ok(name)


def check_section_count(
    sections: list[DocumentSection],
) -> QualityCheckResult:
    name = "parser.section_count"
    if len(sections) < _MIN_SECTIONS_FOR_DOCUMENT:
        return QualityCheckResult.warn(
            name,
            f"Document has only {len(sections)} section(s); expected at least {_MIN_SECTIONS_FOR_DOCUMENT}",
            details={"section_count": len(sections)},
        )
    return QualityCheckResult.ok(name)
