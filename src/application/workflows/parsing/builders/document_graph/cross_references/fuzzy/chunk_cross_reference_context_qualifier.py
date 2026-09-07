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

_CONFIDENCE_ANCHOR_AND_LEAD_IN_AND_TARGET = 0.95
_CONFIDENCE_ANCHOR_AND_TARGET = 0.8
_CONFIDENCE_LEAD_IN_AND_TARGET = 0.75
_CONFIDENCE_GENERIC_CAUTIOUS = 0.45
_CONFIDENCE_EXTERNAL_ANCHOR = 0.85
_CONFIDENCE_CONFLICTING_ANCHORS = 0.4
_CONFIDENCE_ANCHOR_WITHOUT_TARGET = 0.45
_CONFIDENCE_LEAD_IN_WITHOUT_TARGET = 0.35
_CONFIDENCE_NO_SIGNAL = 0.3


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


# Matches a sentence-ending punctuation mark followed by whitespace (or end
# of string) -- used to find the sentence boundaries immediately around a
# reference match, not the whole chunk.
_SENTENCE_END_PATTERN = re.compile(r"[.!?](?:\s+|$)")


def extract_local_reference_context(content: str, span: tuple[int, int]) -> str:
    """The sentence containing `span` within `content`, nothing more. A
    chunk routinely contains several unrelated sentences -- an anchor
    belonging to one reference (e.g. a nearby external standard citation)
    must not leak into the qualification of a different reference
    elsewhere in the same chunk. Falls back to the whole content if no
    sentence boundary is found (e.g. a single-sentence chunk, or a match
    spanning the entire content)."""
    start, end = span

    left_bound = 0
    for boundary in _SENTENCE_END_PATTERN.finditer(content, 0, start):
        left_bound = boundary.end()

    right_boundary = _SENTENCE_END_PATTERN.search(content, end)
    right_bound = right_boundary.end() if right_boundary else len(content)

    return content[left_bound:right_bound]


class ChunkCrossReferenceContextQualifier:
    """Decides whether a detected section/chapter reference actually points
    within the current document (INTERNAL), clearly cites something else
    (EXTERNAL), or can't be told apart from the text alone (AMBIGUOUS).

    Detection only proves a phrase was found -- it never proves the number
    belongs to *this* document. This is the deliberate second stage that
    keeps detection recall-oriented (see chunk_cross_reference_detector.py)
    without letting every match straight through to resolution.

    Target-existence (does this label actually appear in the current
    document's own section numbering) is a REQUIRED condition for INTERNAL,
    not just a confidence booster -- an anchor or lead-in phrase can make a
    reference *look* internal, but only a real target confirms it. Rules,
    in order:
    1. Both anchor types present -> genuinely conflicting signal -> AMBIGUOUS
       rather than guessing.
    2. An external anchor with no internal anchor to counter it -> EXTERNAL,
       regardless of lead-in strength or target existence.
    3. An internal anchor with an existing target -> INTERNAL (highest
       confidence when the lead-in itself is also explicit). An internal
       anchor with NO existing target is withheld as AMBIGUOUS -- the
       wording reads internal, but nothing confirms it actually is.
    4. No anchors either way: an explicit lead-in ("see section", "refer to
       section", "with reference to section", "described in section",
       "chap.") with an existing target -> INTERNAL. Without a target, that
       same explicit lead-in is now AMBIGUOUS too -- lead-in phrasing alone
       is no longer sufficient without corroboration.
    5. A bare "section N"/"chapter N" with no lead-in, no anchors: an
       existing target still promotes it to INTERNAL, but at the lowest,
       most cautious confidence tier (existence alone doesn't rule out
       coincidence with an external citation). No target -> AMBIGUOUS.
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

        if has_internal_anchor:
            if not target_exists_in_document:
                return CrossReferenceQualification(
                    scope=CrossReferenceScope.AMBIGUOUS,
                    confidence=_CONFIDENCE_ANCHOR_WITHOUT_TARGET,
                    reasons=(
                        "internal_anchor_present",
                        "target_section_not_found_in_document",
                    ),
                )
            reasons = ["internal_anchor_present", "target_section_exists_in_document"]
            if is_explicit_lead_in:
                reasons.append("explicit_internal_lead_in")
                confidence = _CONFIDENCE_ANCHOR_AND_LEAD_IN_AND_TARGET
            else:
                confidence = _CONFIDENCE_ANCHOR_AND_TARGET
            return CrossReferenceQualification(
                scope=CrossReferenceScope.INTERNAL,
                confidence=confidence,
                reasons=tuple(reasons),
            )

        if is_explicit_lead_in:
            if not target_exists_in_document:
                return CrossReferenceQualification(
                    scope=CrossReferenceScope.AMBIGUOUS,
                    confidence=_CONFIDENCE_LEAD_IN_WITHOUT_TARGET,
                    reasons=(
                        "explicit_internal_lead_in",
                        "target_section_not_found_in_document",
                    ),
                )
            return CrossReferenceQualification(
                scope=CrossReferenceScope.INTERNAL,
                confidence=_CONFIDENCE_LEAD_IN_AND_TARGET,
                reasons=(
                    "explicit_internal_lead_in",
                    "target_section_exists_in_document",
                ),
            )

        if target_exists_in_document:
            return CrossReferenceQualification(
                scope=CrossReferenceScope.INTERNAL,
                confidence=_CONFIDENCE_GENERIC_CAUTIOUS,
                reasons=("generic_bare_mention", "target_section_exists_in_document"),
            )

        return CrossReferenceQualification(
            scope=CrossReferenceScope.AMBIGUOUS,
            confidence=_CONFIDENCE_NO_SIGNAL,
            reasons=("generic_bare_mention", "no_corroborating_signal"),
        )


__all__ = ["ChunkCrossReferenceContextQualifier", "extract_local_reference_context"]
