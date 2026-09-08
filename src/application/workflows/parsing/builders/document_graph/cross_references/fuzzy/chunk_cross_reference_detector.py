from __future__ import annotations

import re
from dataclasses import dataclass

# Page-number references: unambiguous, resolvable against a precise page
# lookup. Corpus-verified counts: "(-> Page N)" 1304, "see chapter X.X ...,
# Page N" 167, "(see page N)" 18, "see page N" 50 -- checked in this
# priority order so the more specific/complete match wins a span before a
# weaker pattern can also claim part of it (e.g. "see chapter 2.3 ..., Page
# 16" must be captured whole, not just as a bare "see chapter 2.3" section
# reference). Deliberately excludes bare "page N" / "p. N": corpus-verified
# these are ~85%+ PDF pagination footer noise ("Page 1 of 2", "p. 1/10"),
# not same-document navigation.
_PAGE_REFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\(\s*→\s*Page\s*(\d+)\s*\)", re.IGNORECASE),
    re.compile(
        r"\bsee\s+chapter\s+\d+(?:\.\d+)*[^.]{0,60}?,?\s*page\s*(\d+)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\(\s*see\s+page\s*(\d+)\s*\)", re.IGNORECASE),
    re.compile(r"\bsee\s+page\s*(\d+)\b", re.IGNORECASE),
)

# Section/chapter-number references with no page number attached: real and
# fairly common (confirmed via corpus spot-checks these are genuine
# same-document navigation, e.g. "Refer to chap. 8.9 to access..."), but
# deliberately detected-only in v1 -- see
# ChunkCrossReferenceType.SECTION_REFERENCE. Resolving these requires fuzzy
# matching against section numbering/titles, not a page lookup, and is
# deferred to a follow-up phase once the page-based path is proven. Checked
# only against text not already consumed by a page-reference match above, so
# a combined "see chapter X.X ..., Page N" match isn't also double-recorded
# as a separate, redundant section-only reference.
#
# Detection is deliberately recall-oriented and covers several generic,
# domain-independent lead-in phrasings -- corpus review (a real 98-page
# manual) found genuine internal references phrased as "with reference to
# section 9.4" and "described in section 6.5 of this user manual" that a
# narrower "see section"/"see chapter" list misses entirely. Detection is
# NOT acceptance: a bare "Section 1.2" can just as easily cite an external
# standard/directive ("...Annex I, Section 1.2 Controls..."). That
# distinction is ChunkCrossReferenceContextQualifier's job, downstream of
# detection -- see DetectedSectionReference.is_explicit_lead_in below.
_EXPLICIT_SECTION_REFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsee\s+section\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\bsee\s+chapter\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\brefer(?:s|red)?\s+to\s+section\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\brefer(?:s|red)?\s+to\s+chapter\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(
        r"\bwith\s+reference\s+to\s+section\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE
    ),
    re.compile(
        r"\bwith\s+reference\s+to\s+chapter\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE
    ),
    re.compile(r"\bdescribed\s+in\s+section\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\bdescribed\s+in\s+chapter\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\bchap\.\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
)

_GENERIC_SECTION_REFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsection\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\bchapter\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
)

_ANNEX_LABEL = r"(\d+(?:\.\d+)*|[A-Za-z])"
_EXPLICIT_ANNEX_REFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(rf"\bsee\s+annex\s*{_ANNEX_LABEL}\b", re.IGNORECASE),
    re.compile(rf"\bsee\s+appendix\s*{_ANNEX_LABEL}\b", re.IGNORECASE),
    re.compile(rf"\brefer(?:s|red)?\s+to\s+annex\s*{_ANNEX_LABEL}\b", re.IGNORECASE),
    re.compile(rf"\brefer(?:s|red)?\s+to\s+appendix\s*{_ANNEX_LABEL}\b", re.IGNORECASE),
    re.compile(
        rf"\bwith\s+reference\s+to\s+annex\s*{_ANNEX_LABEL}\b", re.IGNORECASE
    ),
    re.compile(
        rf"\bwith\s+reference\s+to\s+appendix\s*{_ANNEX_LABEL}\b", re.IGNORECASE
    ),
    re.compile(rf"\bdescribed\s+in\s+annex\s*{_ANNEX_LABEL}\b", re.IGNORECASE),
    re.compile(rf"\bdescribed\s+in\s+appendix\s*{_ANNEX_LABEL}\b", re.IGNORECASE),
)
# A bare "Annex 2"/"Appendix B" with no lead-in -- weakest signal, same
# treatment as the generic bare section pattern: detected for recall, never
# accepted on the strength of the match alone.
_GENERIC_ANNEX_REFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(rf"\bannex\s*{_ANNEX_LABEL}\b", re.IGNORECASE),
    re.compile(rf"\bappendix\s*{_ANNEX_LABEL}\b", re.IGNORECASE),
)

_TABLE_REFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\btable\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
)
_FIGURE_REFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bfig(?:ure)?\.?\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
)

_MAX_PLAUSIBLE_PAGE = 20_000


@dataclass(slots=True, frozen=True)
class DetectedPageReference:
    matched_text: str
    target_page: int


@dataclass(slots=True, frozen=True)
class DetectedSectionReference:
    matched_text: str
    target_section_label: str

    span: tuple[int, int]

    is_explicit_lead_in: bool = True


@dataclass(slots=True, frozen=True)
class DetectedAnnexReference:
    matched_text: str
    target_annex_label: str

    span: tuple[int, int]

    is_explicit_lead_in: bool = True


@dataclass(slots=True, frozen=True)
class DetectedAssetReference:
    matched_text: str
    target_asset_label: str


@dataclass(slots=True, frozen=True)
class ChunkReferenceDetectionResult:
    page_references: list[DetectedPageReference]
    section_references: list[DetectedSectionReference]
    annex_references: list[DetectedAnnexReference]
    table_references: list[DetectedAssetReference]
    figure_references: list[DetectedAssetReference]


class ChunkCrossReferenceDetector:

    def detect(self, content: str) -> ChunkReferenceDetectionResult:
        if not content:
            return ChunkReferenceDetectionResult(
                page_references=[],
                section_references=[],
                annex_references=[],
                table_references=[],
                figure_references=[],
            )

        consumed_spans: list[tuple[int, int]] = []
        page_references = self._detect_page_references(content, consumed_spans)
        section_references = self._detect_section_references(content, consumed_spans)
        annex_references = self._detect_annex_references(content, consumed_spans)
        table_references = self._detect_asset_references(
            content, consumed_spans, _TABLE_REFERENCE_PATTERNS
        )
        figure_references = self._detect_asset_references(
            content, consumed_spans, _FIGURE_REFERENCE_PATTERNS
        )

        return ChunkReferenceDetectionResult(
            page_references=page_references,
            section_references=section_references,
            annex_references=annex_references,
            table_references=table_references,
            figure_references=figure_references,
        )

    def _detect_page_references(
        self, content: str, consumed_spans: list[tuple[int, int]]
    ) -> list[DetectedPageReference]:
        references: list[DetectedPageReference] = []

        for pattern in _PAGE_REFERENCE_PATTERNS:
            for match in pattern.finditer(content):
                span = match.span()
                if self._overlaps_any(span, consumed_spans):
                    continue

                target_page = self._parse_plausible_page(match.group(1))
                if target_page is None:
                    continue

                consumed_spans.append(span)
                references.append(
                    DetectedPageReference(
                        matched_text=match.group(0).strip(),
                        target_page=target_page,
                    )
                )

        return references

    def _detect_section_references(
        self, content: str, consumed_spans: list[tuple[int, int]]
    ) -> list[DetectedSectionReference]:
        references: list[DetectedSectionReference] = []

        for pattern in _EXPLICIT_SECTION_REFERENCE_PATTERNS:
            for match in pattern.finditer(content):
                span = match.span()
                if self._overlaps_any(span, consumed_spans):
                    continue

                consumed_spans.append(span)
                references.append(
                    DetectedSectionReference(
                        matched_text=match.group(0).strip(),
                        target_section_label=match.group(1),
                        span=span,
                        is_explicit_lead_in=True,
                    )
                )

        for pattern in _GENERIC_SECTION_REFERENCE_PATTERNS:
            for match in pattern.finditer(content):
                span = match.span()
                if self._overlaps_any(span, consumed_spans):
                    continue

                consumed_spans.append(span)
                references.append(
                    DetectedSectionReference(
                        matched_text=match.group(0).strip(),
                        target_section_label=match.group(1),
                        span=span,
                        is_explicit_lead_in=False,
                    )
                )

        return references

    def _detect_annex_references(
        self, content: str, consumed_spans: list[tuple[int, int]]
    ) -> list[DetectedAnnexReference]:
        references: list[DetectedAnnexReference] = []

        for pattern in _EXPLICIT_ANNEX_REFERENCE_PATTERNS:
            for match in pattern.finditer(content):
                span = match.span()
                if self._overlaps_any(span, consumed_spans):
                    continue

                consumed_spans.append(span)
                references.append(
                    DetectedAnnexReference(
                        matched_text=match.group(0).strip(),
                        target_annex_label=match.group(1),
                        span=span,
                        is_explicit_lead_in=True,
                    )
                )

        for pattern in _GENERIC_ANNEX_REFERENCE_PATTERNS:
            for match in pattern.finditer(content):
                span = match.span()
                if self._overlaps_any(span, consumed_spans):
                    continue

                consumed_spans.append(span)
                references.append(
                    DetectedAnnexReference(
                        matched_text=match.group(0).strip(),
                        target_annex_label=match.group(1),
                        span=span,
                        is_explicit_lead_in=False,
                    )
                )

        return references

    @staticmethod
    def _detect_asset_references(
        content: str,
        consumed_spans: list[tuple[int, int]],
        patterns: tuple[re.Pattern[str], ...],
    ) -> list[DetectedAssetReference]:
        references: list[DetectedAssetReference] = []

        for pattern in patterns:
            for match in pattern.finditer(content):
                span = match.span()
                if ChunkCrossReferenceDetector._overlaps_any(span, consumed_spans):
                    continue

                consumed_spans.append(span)
                references.append(
                    DetectedAssetReference(
                        matched_text=match.group(0).strip(),
                        target_asset_label=match.group(1),
                    )
                )

        return references

    @staticmethod
    def _parse_plausible_page(raw_value: str) -> int | None:
        try:
            page = int(raw_value)
        except ValueError:
            return None

        if page <= 0 or page > _MAX_PLAUSIBLE_PAGE:
            return None

        return page

    @staticmethod
    def _overlaps_any(span: tuple[int, int], other_spans: list[tuple[int, int]]) -> bool:
        start, end = span
        return any(start < other_end and end > other_start for other_start, other_end in other_spans)


__all__ = [
    "ChunkCrossReferenceDetector",
    "ChunkReferenceDetectionResult",
    "DetectedAnnexReference",
    "DetectedAssetReference",
    "DetectedPageReference",
    "DetectedSectionReference",
]
