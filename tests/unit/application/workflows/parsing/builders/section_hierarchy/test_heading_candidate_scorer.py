from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates import (
    HeadingCandidateRole,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_scorer import (
    HeadingCandidateScorer,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_signals import (
    HeadingCandidateSignals,
)
from src.domain.common import ElementType


def _signals(**overrides) -> HeadingCandidateSignals:
    values = {
        "numbering": None,
        "numbering_depth": None,
        "active_scope_depth": None,
        "numbering_compatible": None,
        "implausible_hierarchy_jump": False,
        "toc_matched": False,
        "toc_title_exact": False,
        "toc_number_exact": False,
        "toc_page_close": False,
        "native_heading_level": None,
        "has_descendant_pattern": False,
        "has_sibling_pattern": False,
        "next_element_type": None,
        "next_element_same_page": False,
        "next_element_order_gap": None,
        "repeated_title_count": 1,
        "embedded_item_numbering": False,
        "layout_prominent": False,
        "indented_from_active": False,
        "page_continuous": True,
        "caption_like": False,
        "noise_like": False,
        "title_word_count": 3,
        "ends_with_colon": False,
    }
    values.update(overrides)
    return HeadingCandidateSignals(**values)


def test_adjacent_table_and_incompatible_scope_outweigh_toc_alone() -> None:
    assessment = HeadingCandidateScorer().assess(
        _signals(
            numbering="17",
            numbering_depth=1,
            active_scope_depth=2,
            numbering_compatible=False,
            toc_matched=True,
            toc_title_exact=True,
            next_element_type=ElementType.TABLE,
            next_element_same_page=True,
            next_element_order_gap=1,
        )
    )

    assert assessment.role == HeadingCandidateRole.TABLE_CATEGORY


def test_agreeing_toc_numbering_and_descendants_produce_outline_section() -> None:
    assessment = HeadingCandidateScorer().assess(
        _signals(
            numbering="5",
            numbering_depth=1,
            active_scope_depth=2,
            numbering_compatible=True,
            toc_matched=True,
            toc_title_exact=True,
            toc_number_exact=True,
            toc_page_close=True,
            native_heading_level=1,
            has_descendant_pattern=True,
            has_sibling_pattern=True,
        )
    )

    assert assessment.role == HeadingCandidateRole.OUTLINE_SECTION


def test_ambiguous_candidate_defaults_to_outline_to_avoid_content_loss() -> None:
    assessment = HeadingCandidateScorer().assess(_signals())

    assert assessment.role == HeadingCandidateRole.OUTLINE_SECTION


def test_caption_and_furniture_are_not_outline_sections() -> None:
    scorer = HeadingCandidateScorer()

    assert scorer.assess(_signals(caption_like=True)).role == HeadingCandidateRole.CAPTION
    assert scorer.assess(_signals(noise_like=True)).role == HeadingCandidateRole.NOISE
