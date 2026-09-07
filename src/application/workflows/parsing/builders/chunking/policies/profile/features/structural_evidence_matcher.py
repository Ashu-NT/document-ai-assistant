from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)

# Crude title-keyword lists feeding the "structural_evidence" signal used by
# StructuralProfileInferer/HybridDocumentTypeResolver -- deliberately separate
# from the typed EvidenceMarker/MarkerStrength catalogs under
# chunking/builders/structured/markers, which score evidence within
# already-classified section content, not raw title keyword density across
# a whole document.
_MANUAL_STRUCTURAL_EVIDENCE_TERMS = (
    "maintenance",
    "procedure",
    "task",
    "operation",
    "installation",
    "troubleshooting",
    "service",
    "inspection",
    "repair",
)
_DATASHEET_STRUCTURAL_EVIDENCE_TERMS = (
    "datasheet",
    "technical data",
    "technical specification",
    "specification",
    "specifications",
    "electrical",
    "mechanical",
    "rating",
    "ratings",
    "dimensions",
)
_DRAWING_STRUCTURAL_EVIDENCE_TERMS = (
    "drawing",
    "schematic",
    "diagram",
    "layout",
    "wiring",
)
_REPORT_STRUCTURAL_EVIDENCE_TERMS = (
    "abstract",
    "results",
    "discussion",
    "conclusion",
    "conclusions",
    "background",
    "methodology",
    "method",
)
_CERTIFICATE_STRUCTURAL_EVIDENCE_TERMS = (
    "certificate",
    "conformity",
    "certification",
    "inspection certificate",
    "test certificate",
    "certificate of conformity",
)

_DEFAULT_TERM_CATALOG: dict[ChunkingProfile, tuple[str, ...]] = {
    ChunkingProfile.MANUAL: _MANUAL_STRUCTURAL_EVIDENCE_TERMS,
    ChunkingProfile.DATASHEET: _DATASHEET_STRUCTURAL_EVIDENCE_TERMS,
    ChunkingProfile.DRAWING: _DRAWING_STRUCTURAL_EVIDENCE_TERMS,
    ChunkingProfile.REPORT: _REPORT_STRUCTURAL_EVIDENCE_TERMS,
    ChunkingProfile.CERTIFICATE: _CERTIFICATE_STRUCTURAL_EVIDENCE_TERMS,
}


@dataclass(slots=True, frozen=True)
class StructuralEvidenceSummary:
    total_occurrences: int = 0
    distinct_term_count: int = 0
    matching_title_count: int = 0
    matched_terms: tuple[str, ...] = ()


class StructuralEvidenceMatcher:
    """Crude substring-based per-profile evidence matching against
    section/document TITLES. Deliberately separate from the typed
    EvidenceMarker/MarkerStrength catalogs under
    chunking/builders/structured/markers, which score evidence within
    already-classified section content, not raw title term density across
    a whole document."""

    def __init__(
        self,
        term_catalog: dict[ChunkingProfile, tuple[str, ...]] | None = None,
    ) -> None:
        self.term_catalog = term_catalog or _DEFAULT_TERM_CATALOG

    def match(
        self,
        titles: list[str],
    ) -> dict[ChunkingProfile, StructuralEvidenceSummary]:
        return {
            profile: self._match_terms(titles, terms)
            for profile, terms in self.term_catalog.items()
        }

    @staticmethod
    def _match_terms(
        titles: list[str],
        terms: tuple[str, ...],
    ) -> StructuralEvidenceSummary:
        total_occurrences = 0
        matching_title_count = 0
        matched_terms: set[str] = set()

        for title in titles:
            title_matched = False
            for term in terms:
                if term in title:
                    total_occurrences += 1
                    matched_terms.add(term)
                    title_matched = True
            if title_matched:
                matching_title_count += 1

        return StructuralEvidenceSummary(
            total_occurrences=total_occurrences,
            distinct_term_count=len(matched_terms),
            matching_title_count=matching_title_count,
            matched_terms=tuple(sorted(matched_terms)),
        )
