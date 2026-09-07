from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_context_qualifier import (
    ChunkCrossReferenceContextQualifier,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.cross_reference_qualification import (
    CrossReferenceScope,
)


def _qualifier() -> ChunkCrossReferenceContextQualifier:
    return ChunkCrossReferenceContextQualifier()


def test_explicit_lead_in_with_no_anchors_is_internal() -> None:
    # Real document (corpus review): "With reference to section 9.4, item
    # 13 above, refit the end shield..." -- no "this manual"-style anchor
    # anywhere nearby, but the explicit lead-in phrase is trusted on its
    # own, preserving today's accepted behavior for "see section"/"chap."
    result = _qualifier().qualify_section_reference(
        is_explicit_lead_in=True,
        context_text="With reference to section 9.4, item 13 above, refit the end shield.",
        target_exists_in_document=True,
    )

    assert result.scope == CrossReferenceScope.INTERNAL
    assert "explicit_internal_lead_in" in result.reasons


def test_explicit_lead_in_confidence_rises_with_an_internal_anchor() -> None:
    without_anchor = _qualifier().qualify_section_reference(
        is_explicit_lead_in=True,
        context_text="Refer to section 5.2 for calibration steps.",
        target_exists_in_document=False,
    )
    with_anchor = _qualifier().qualify_section_reference(
        is_explicit_lead_in=True,
        context_text="Refer to section 5.2 of this manual for calibration steps.",
        target_exists_in_document=False,
    )

    assert without_anchor.scope == CrossReferenceScope.INTERNAL
    assert with_anchor.scope == CrossReferenceScope.INTERNAL
    assert with_anchor.confidence > without_anchor.confidence


def test_external_anchor_overrides_even_an_explicit_lead_in() -> None:
    # A deliberate behavior change: previously any "see section N" would
    # have gone straight to resolution regardless of context. A named
    # external standards-body reference sitting right next to it is now
    # enough to withhold it, rather than risk cross-linking to an unrelated
    # internal section that happens to share the same number.
    result = _qualifier().qualify_section_reference(
        is_explicit_lead_in=True,
        context_text="See section 5 of the ISO 9001 standard for details.",
        target_exists_in_document=True,
    )

    assert result.scope == CrossReferenceScope.EXTERNAL
    assert "external_anchor_present" in result.reasons


def test_bare_generic_mention_citing_an_external_directive_is_external() -> None:
    # Real document (corpus review): "...latest version of the EC-Directive
    # for Machinery, Annex I, Section 1.2 Controls should be observed."
    result = _qualifier().qualify_section_reference(
        is_explicit_lead_in=False,
        context_text=(
            "In particular for control systems the latest version of the "
            "Directive for Machinery, Annex I, Section 1.2 Controls should "
            "be observed."
        ),
        target_exists_in_document=True,
    )

    assert result.scope == CrossReferenceScope.EXTERNAL


def test_bare_generic_mention_with_internal_anchor_is_internal_but_lower_confidence_than_explicit() -> (
    None
):
    generic_result = _qualifier().qualify_section_reference(
        is_explicit_lead_in=False,
        context_text="Section 4.2 of this manual covers installation drawings.",
        target_exists_in_document=True,
    )
    explicit_result = _qualifier().qualify_section_reference(
        is_explicit_lead_in=True,
        context_text="Refer to section 4.2 of this manual for installation drawings.",
        target_exists_in_document=True,
    )

    assert generic_result.scope == CrossReferenceScope.INTERNAL
    assert explicit_result.scope == CrossReferenceScope.INTERNAL
    assert generic_result.confidence < explicit_result.confidence


def test_bare_generic_mention_with_existing_target_but_no_anchor_is_weakly_internal() -> (
    None
):
    result = _qualifier().qualify_section_reference(
        is_explicit_lead_in=False,
        context_text="Section 4.2 Installation Drawings",
        target_exists_in_document=True,
    )

    assert result.scope == CrossReferenceScope.INTERNAL
    assert "target_section_exists_in_document" in result.reasons


def test_bare_generic_mention_with_no_target_and_no_anchor_is_ambiguous() -> None:
    # No positive evidence either way -- the conservative default is to not
    # resolve, not to confidently guess EXTERNAL either.
    result = _qualifier().qualify_section_reference(
        is_explicit_lead_in=False,
        context_text="Section 12.9 was updated last year.",
        target_exists_in_document=False,
    )

    assert result.scope == CrossReferenceScope.AMBIGUOUS


def test_conflicting_anchors_are_ambiguous_rather_than_guessed() -> None:
    result = _qualifier().qualify_section_reference(
        is_explicit_lead_in=True,
        context_text=(
            "See section 4.2 of this manual, which mirrors the ISO standard."
        ),
        target_exists_in_document=True,
    )

    assert result.scope == CrossReferenceScope.AMBIGUOUS
    assert "internal_anchor_present" in result.reasons
    assert "external_anchor_present" in result.reasons


def test_every_qualification_carries_at_least_one_reason() -> None:
    for is_explicit in (True, False):
        for target_exists in (True, False):
            result = _qualifier().qualify_section_reference(
                is_explicit_lead_in=is_explicit,
                context_text="Section 3 has no anchors at all.",
                target_exists_in_document=target_exists,
            )
            assert len(result.reasons) > 0
