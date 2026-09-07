from __future__ import annotations

import re

from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.cross_reference_qualification import (
    CrossReferenceQualification,
    CrossReferenceScope,
)

# Generic, domain-independent phrases that say "the document you are
# currently reading" -- never tuned to any one manual's wording.
_INTERNAL_ANCHOR_MARKERS: tuple[str, ...] = (
    "this manual",
    "this document",
    "this instruction",
    "this user manual",
    "this instruction manual",
    "of this manual",
    "in this manual",
)

# Generic markers for an external standard/directive/regulation being
# quoted or cited -- genre-level vocabulary common across technical/
# industrial manuals in general, not specific to any one document's own
# wording. A named standards-body acronym or "directive"/"regulation"/
# "standard" sitting next to a section/chapter number is a strong signal
# the number belongs to THAT external text, not this one.
_EXTERNAL_ANCHOR_MARKERS: tuple[str, ...] = (
    "directive",
    "regulation",
    "standard",
    "iso ",
    "iec ",
    "din ",
    "ansi ",
    "atex",
    "nfpa",
    "asme",
)

_CONFIDENCE_EXPLICIT_DEFAULT = 0.7
_CONFIDENCE_EXPLICIT_CORROBORATED = 0.9
_CONFIDENCE_EXTERNAL_ANCHOR = 0.85
_CONFIDENCE_CONFLICTING_ANCHORS = 0.4
_CONFIDENCE_GENERIC_WITH_INTERNAL_ANCHOR = 0.65
_CONFIDENCE_GENERIC_WITH_EXISTING_TARGET = 0.45
_CONFIDENCE_GENERIC_UNCORROBORATED = 0.3


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


class ChunkCrossReferenceContextQualifier:
    """Decides whether a detected section/chapter reference actually points
    within the current document (INTERNAL), clearly cites something else
    (EXTERNAL), or can't be told apart from the text alone (AMBIGUOUS).

    Detection only proves a phrase was found -- it never proves the number
    belongs to *this* document. This is the deliberate second stage that
    keeps detection recall-oriented (see chunk_cross_reference_detector.py)
    without letting every match straight through to resolution.

    Rules, in order:
    1. An external anchor with no internal anchor to counter it -> EXTERNAL.
    2. Both anchor types present -> genuinely conflicting signal -> AMBIGUOUS
       rather than guessing.
    3. An explicit navigational lead-in ("see section", "refer to section",
       "with reference to section", "described in section", "chap.") is
       trusted on its own -- this preserves today's accepted behavior for
       the patterns that already existed before this qualifier was added.
       An internal anchor or an existing target simply raises confidence.
    4. A bare "section N"/"chapter N" with no lead-in is corroborated, never
       trusted alone: an internal anchor promotes it to INTERNAL (higher
       confidence); failing that, the target number actually existing in
       this document's own numbering promotes it too (lower confidence --
       existence alone doesn't rule out coincidence with an external
       citation); with neither, it's AMBIGUOUS, not confidently EXTERNAL --
       there's no positive evidence either way, and "don't resolve" is the
       same safe outcome either way.
    """

    def qualify_section_reference(
        self,
        *,
        is_explicit_lead_in: bool,
        context_text: str,
        target_exists_in_document: bool,
    ) -> CrossReferenceQualification:
        normalized_context = _normalize(context_text)
        has_internal_anchor = any(
            marker in normalized_context for marker in _INTERNAL_ANCHOR_MARKERS
        )
        has_external_anchor = any(
            marker in normalized_context for marker in _EXTERNAL_ANCHOR_MARKERS
        )

        if has_external_anchor and has_internal_anchor:
            return CrossReferenceQualification(
                scope=CrossReferenceScope.AMBIGUOUS,
                confidence=_CONFIDENCE_CONFLICTING_ANCHORS,
                reasons=("internal_anchor_present", "external_anchor_present"),
            )

        if has_external_anchor:
            return CrossReferenceQualification(
                scope=CrossReferenceScope.EXTERNAL,
                confidence=_CONFIDENCE_EXTERNAL_ANCHOR,
                reasons=("external_anchor_present",),
            )

        if is_explicit_lead_in:
            reasons = ["explicit_internal_lead_in"]
            if has_internal_anchor:
                reasons.append("internal_anchor_present")
            if target_exists_in_document:
                reasons.append("target_section_exists_in_document")
            confidence = (
                _CONFIDENCE_EXPLICIT_CORROBORATED
                if (has_internal_anchor or target_exists_in_document)
                else _CONFIDENCE_EXPLICIT_DEFAULT
            )
            return CrossReferenceQualification(
                scope=CrossReferenceScope.INTERNAL,
                confidence=confidence,
                reasons=tuple(reasons),
            )

        if has_internal_anchor:
            return CrossReferenceQualification(
                scope=CrossReferenceScope.INTERNAL,
                confidence=_CONFIDENCE_GENERIC_WITH_INTERNAL_ANCHOR,
                reasons=("generic_bare_mention", "internal_anchor_present"),
            )

        if target_exists_in_document:
            return CrossReferenceQualification(
                scope=CrossReferenceScope.INTERNAL,
                confidence=_CONFIDENCE_GENERIC_WITH_EXISTING_TARGET,
                reasons=("generic_bare_mention", "target_section_exists_in_document"),
            )

        return CrossReferenceQualification(
            scope=CrossReferenceScope.AMBIGUOUS,
            confidence=_CONFIDENCE_GENERIC_UNCORROBORATED,
            reasons=("generic_bare_mention", "no_corroborating_signal"),
        )


__all__ = ["ChunkCrossReferenceContextQualifier"]
