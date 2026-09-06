from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.builders.structured.arbitration.structured_reference_evidence_policy import (
    StructuredReferenceEvidencePolicy,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.arbitration.structured_section_context_policy import (
    StructuredSectionContextPolicy,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.arbitration.structured_window_candidate import (
    StructuredWindowCandidate,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.arbitration.structured_window_evidence_scorer import (
    StructuredWindowEvidenceScorer,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.qualification_policy import (
    StructuredMarkerQualificationPolicy,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    MarkerMatch,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.markers.structured_marker_match_policy import (
    StructuredMarkerMatchPolicy,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_element_text_resolver import (
    StructuredElementTextResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_section_window_spec import (
    StructuredSectionWindowSpec,
)
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


@dataclass(frozen=True, slots=True)
class _MatchedAnchor:
    index: int
    element_id: str
    matches: tuple[MarkerMatch, ...]
    reference_only: bool


class StructuredWindowCandidateBuilder:
    def __init__(
        self,
        *,
        marker_match_policy: StructuredMarkerMatchPolicy,
        qualification_policy: StructuredMarkerQualificationPolicy | None = None,
        reference_policy: StructuredReferenceEvidencePolicy,
        evidence_scorer: StructuredWindowEvidenceScorer | None = None,
        section_context_policy: StructuredSectionContextPolicy | None = None,
    ) -> None:
        self.marker_match_policy = marker_match_policy
        self.qualification_policy = qualification_policy or StructuredMarkerQualificationPolicy()
        self.reference_policy = reference_policy
        self.evidence_scorer = evidence_scorer or StructuredWindowEvidenceScorer()
        self.section_context_policy = section_context_policy or (
            StructuredSectionContextPolicy(marker_match_policy=marker_match_policy)
        )

    def build(
        self,
        *,
        section: DocumentSection,
        elements: list[CanonicalElement],
        specs: list[StructuredSectionWindowSpec],
    ) -> list[StructuredWindowCandidate]:
        candidates: list[StructuredWindowCandidate] = []
        for spec in specs:
            anchors = self._matched_anchors(elements, spec)
            windows = self._windows(elements, spec, anchors)
            local_section_context = self.section_context_policy.matches_local_section(
                section=section,
                spec=spec,
            )
            for window, window_anchors in windows:
                has_direct_evidence = self.evidence_scorer.has_direct_evidence(
                    spec=spec,
                    elements=window,
                )
                if not window_anchors and not (local_section_context or has_direct_evidence):
                    continue
                qualification = self.qualification_policy.qualify(
                    matches=tuple(match for anchor in window_anchors for match in anchor.matches),
                    section_context_matches=(
                        local_section_context
                        or (spec.section_context_matches and bool(window_anchors))
                        or has_direct_evidence
                    ),
                )
                if window_anchors and not qualification.qualified:
                    continue
                marker_score = qualification.score
                score, direct_evidence = self.evidence_scorer.score(
                    section=section,
                    spec=spec,
                    elements=window,
                    marker_score=marker_score,
                    local_section_context=local_section_context,
                )
                reference_only = bool(window_anchors) and all(
                    anchor.reference_only for anchor in window_anchors
                )
                if reference_only and not direct_evidence:
                    continue
                candidates.append(
                    StructuredWindowCandidate(
                        spec=spec,
                        elements=window,
                        anchor_element_ids=frozenset(
                            anchor.element_id for anchor in window_anchors
                        ),
                        score=score,
                        direct_evidence=direct_evidence,
                        reference_only=reference_only,
                    )
                )
        return candidates

    def _matched_anchors(
        self,
        elements: list[CanonicalElement],
        spec: StructuredSectionWindowSpec,
    ) -> list[_MatchedAnchor]:
        anchors: list[_MatchedAnchor] = []
        for index, element in enumerate(elements):
            text = StructuredElementTextResolver.resolve(element) or ""
            matches = self.marker_match_policy.find_matches(text, spec.anchor_markers)
            if not matches:
                continue
            anchors.append(
                _MatchedAnchor(
                    index=index,
                    element_id=element.element_id,
                    matches=matches,
                    reference_only=self.reference_policy.is_reference_only(text, matches),
                )
            )
        return anchors

    def _windows(
        self,
        elements: list[CanonicalElement],
        spec: StructuredSectionWindowSpec,
        anchors: list[_MatchedAnchor],
    ) -> list[tuple[tuple[CanonicalElement, ...], tuple[_MatchedAnchor, ...]]]:
        if not anchors:
            if spec.include_full_section_if_no_anchor and elements:
                return [(tuple(elements), tuple())]
            return []

        ranges = self._merge_ranges(
            [
                (
                    max(0, anchor.index - spec.radius_before),
                    min(len(elements) - 1, anchor.index + spec.radius_after),
                )
                for anchor in anchors
            ]
        )
        if spec.combine_all_windows:
            combined_elements: list[CanonicalElement] = []
            seen_element_ids: set[str] = set()
            for start, end in ranges:
                for element in elements[start : end + 1]:
                    if element.element_id in seen_element_ids:
                        continue
                    seen_element_ids.add(element.element_id)
                    combined_elements.append(element)
            return [(tuple(combined_elements), tuple(anchors))]
        return [
            (
                tuple(elements[start : end + 1]),
                tuple(anchor for anchor in anchors if start <= anchor.index <= end),
            )
            for start, end in ranges
        ]

    @staticmethod
    def _merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not ranges:
            return []
        merged = [min(ranges)]
        for start, end in sorted(ranges)[1:]:
            previous_start, previous_end = merged[-1]
            if start <= previous_end + 1:
                merged[-1] = (previous_start, max(previous_end, end))
            else:
                merged.append((start, end))
        return merged
