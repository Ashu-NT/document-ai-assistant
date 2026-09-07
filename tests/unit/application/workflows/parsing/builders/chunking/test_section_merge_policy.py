from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge.section_merge_policy import (
    SectionMergePolicy,
)
from src.domain.common import ChunkType


def make_fragment(
    *,
    text: str,
    section_id: str,
    section_title: str,
    section_path: list[str],
    section_level: int,
    parent_section_id: str | None,
    token_count: int,
) -> ChunkFragment:
    return ChunkFragment(
        text=text,
        chunk_type=ChunkType.GENERAL,
        section_id=section_id,
        section_title=section_title,
        section_path=section_path,
        section_level=section_level,
        parent_section_id=parent_section_id,
        token_count=token_count,
    )


def make_policy(max_chunk_tokens: int = 200) -> SectionMergePolicy:
    return SectionMergePolicy(
        text_splitter=ChunkTextSplitter(
            max_chunk_tokens=max_chunk_tokens,
            chunk_overlap=20,
        ),
        min_section_text_length=20,
    )


def test_merge_policy_keeps_same_topic_sibling_sections_together() -> None:
    policy = make_policy()
    current_fragment = make_fragment(
        text="Bit manipulation explanation",
        section_id="sec_a",
        section_title="1.2.1 Interrupt handler and bit manipulation",
        section_path=["Chapter 1", "Lab preparation", "1.2.1 Interrupt handler and bit manipulation"],
        section_level=3,
        parent_section_id="sec_parent",
        token_count=95,
    )
    next_fragment = make_fragment(
        text="Prep task question",
        section_id="sec_b",
        section_title="Prep task 1: Interrupt handler and bit manipulation",
        section_path=["Chapter 1", "Lab preparation", "Prep task 1: Interrupt handler and bit manipulation"],
        section_level=3,
        parent_section_id="sec_parent",
        token_count=38,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is False


def test_merge_policy_separates_sections_with_conflicting_hard_families() -> None:
    # "Safety warnings" (safety family) and "Troubleshooting" (procedural
    # family) are a hard veto -- different, incompatible content families
    # must never merge regardless of anything else.
    policy = make_policy()
    current_fragment = make_fragment(
        text="Safety rules",
        section_id="sec_a",
        section_title="Safety warnings",
        section_path=["Manual", "Procedure", "Safety warnings"],
        section_level=3,
        parent_section_id="sec_parent",
        token_count=24,
    )
    next_fragment = make_fragment(
        text="Troubleshooting steps",
        section_id="sec_b",
        section_title="Troubleshooting",
        section_path=["Manual", "Procedure", "Troubleshooting"],
        section_level=3,
        parent_section_id="sec_parent",
        token_count=24,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is True


def test_merge_policy_merges_same_family_siblings_without_shared_topic() -> None:
    # "1.7 Modifications" and "1.8 Liability and Warranty" don't share a
    # topic, but both are the "legal" family -- same family is a valid
    # positive signal on its own (rule 5), so they may merge. This is a
    # deliberate design decision, not a regression: the hard veto is
    # specifically for CROSS-family pairs (see the next test), not for two
    # different clauses of the same kind.
    policy = make_policy()
    current_fragment = make_fragment(
        text="Modifications require written consent.",
        section_id="sec_17",
        section_title="1.7 Modifications",
        section_path=["1 General", "1.7 Modifications"],
        section_level=2,
        parent_section_id="sec_general",
        token_count=24,
    )
    next_fragment = make_fragment(
        text="Liability is limited as described below.",
        section_id="sec_18",
        section_title="1.8 Liability and Warranty",
        section_path=["1 General", "1.8 Liability and Warranty"],
        section_level=2,
        parent_section_id="sec_general",
        token_count=24,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is False


def test_merge_policy_separates_cross_family_numbered_siblings() -> None:
    # Regression for the actual reported bug: numbering alone (both
    # sections numbered, same parent) must never be enough to merge a
    # legal clause with an unrelated procedural/technical section. Unlike
    # the same-family case above, "legal" vs "procedural" is a hard
    # cross-family veto.
    policy = make_policy()
    current_fragment = make_fragment(
        text="Modifications require written consent.",
        section_id="sec_17",
        section_title="1.7 Modifications",
        section_path=["1 General", "1.7 Modifications"],
        section_level=2,
        parent_section_id="sec_general",
        token_count=24,
    )
    next_fragment = make_fragment(
        text="Follow these steps to install the unit.",
        section_id="sec_18",
        section_title="1.8 Installation Procedure",
        section_path=["1 General", "1.8 Installation Procedure"],
        section_level=2,
        parent_section_id="sec_general",
        token_count=24,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is True


def test_merge_policy_separates_bare_numbered_siblings_with_no_topic_text() -> None:
    # Numbering alone is never a merge signal, even when there's nothing
    # else to go on: two bare "Step 1"/"Step 2" siblings with no shared
    # topic and no recognized family must default to separate (the
    # conservative default), not merge just because they're sequential.
    policy = make_policy()
    current_fragment = make_fragment(
        text="Turn off the main valve.",
        section_id="sec_step1",
        section_title="Step 1",
        section_path=["Procedure", "Step 1"],
        section_level=2,
        parent_section_id="sec_procedure",
        token_count=24,
    )
    next_fragment = make_fragment(
        text="Disconnect the power supply.",
        section_id="sec_step2",
        section_title="Step 2",
        section_path=["Procedure", "Step 2"],
        section_level=2,
        parent_section_id="sec_procedure",
        token_count=24,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is True


def test_merge_policy_requires_same_parent_for_sibling_merge() -> None:
    # Two sections can share keywords/topic and still must not merge via
    # the sibling path if they aren't actually siblings (different
    # parents) -- sharing a topic is not a substitute for structural
    # adjacency, and they're not in an ancestor relationship either.
    policy = make_policy()
    current_fragment = make_fragment(
        text="Basics of interrupt handling.",
        section_id="sec_a",
        section_title="Interrupt Handling Basics",
        section_path=["Chapter 1", "Section A", "Interrupt Handling Basics"],
        section_level=3,
        parent_section_id="sec_section_a",
        token_count=24,
    )
    next_fragment = make_fragment(
        text="Advanced interrupt handling techniques.",
        section_id="sec_b",
        section_title="Interrupt Handling Advanced",
        section_path=["Chapter 1", "Section B", "Interrupt Handling Advanced"],
        section_level=3,
        parent_section_id="sec_section_b",
        token_count=24,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is True


def test_merge_policy_keeps_content_within_token_budget() -> None:
    # Even a same-parent, same-topic pair must still separate once the
    # combined content would exceed the chunk's token budget -- the budget
    # gate applies before any positive-signal check runs.
    policy = make_policy(max_chunk_tokens=100)
    current_fragment = make_fragment(
        text="First half of the maintenance procedure.",
        section_id="sec_a",
        section_title="Maintenance Procedure Part 1",
        section_path=["Manual", "Maintenance Procedure Part 1"],
        section_level=2,
        parent_section_id="sec_manual",
        token_count=60,
    )
    next_fragment = make_fragment(
        text="Second half of the maintenance procedure.",
        section_id="sec_b",
        section_title="Maintenance Procedure Part 2",
        section_path=["Manual", "Maintenance Procedure Part 2"],
        section_level=2,
        parent_section_id="sec_manual",
        token_count=60,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is True


def test_merge_policy_keeps_genuine_intro_with_its_child_section() -> None:
    # A parent recognized as introductory (background/overview-style) may
    # fold into its own child section -- the refinement/complement signal
    # from rule 5, independent of whether the child's title shares any
    # topic keywords with the parent.
    policy = make_policy()
    parent_fragment = make_fragment(
        text="This chapter introduces the topic.",
        section_id="sec_parent",
        section_title="Overview",
        section_path=["Chapter 1", "Overview"],
        section_level=2,
        parent_section_id="sec_chapter",
        token_count=40,
    )
    child_fragment = make_fragment(
        text="Specific configuration steps follow.",
        section_id="sec_child",
        section_title="Advanced Configuration",
        section_path=["Chapter 1", "Overview", "Advanced Configuration"],
        section_level=3,
        parent_section_id="sec_parent",
        token_count=60,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[parent_fragment],
        next_fragment=child_fragment,
    )

    assert should_flush is False


def test_merge_policy_does_not_merge_child_into_a_non_introductory_parent() -> None:
    # A parent section whose title isn't recognized introductory language
    # doesn't get treated as scene-setting just because it has a child and
    # is short -- with no shared topic, no shared family, and no
    # recognized "refinement" signal, the conservative default applies.
    policy = make_policy()
    parent_fragment = make_fragment(
        text="Project overview",
        section_id="sec_parent",
        section_title="A first DSP project with Code Composer Studio",
        section_path=["Chapter 1", "A first DSP project with Code Composer Studio"],
        section_level=2,
        parent_section_id="sec_chapter",
        token_count=55,
    )
    child_fragment = make_fragment(
        text="Task instructions",
        section_id="sec_child",
        section_title="Feeding the ADC input directly to the DAC output",
        section_path=[
            "Chapter 1",
            "A first DSP project with Code Composer Studio",
            "Feeding the ADC input directly to the DAC output",
        ],
        section_level=3,
        parent_section_id="sec_parent",
        token_count=80,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[parent_fragment],
        next_fragment=child_fragment,
    )

    assert should_flush is True


def test_merge_policy_blocks_intro_refinement_when_intro_section_is_too_large() -> (
    None
):
    # A section titled "Overview" that has already grown well past a
    # scene-setting size no longer reads as a short intro -- it's
    # substantial content of its own, so it should not keep pulling in its
    # child section regardless of the title match.
    policy = make_policy()
    parent_fragment = make_fragment(
        text="A very long overview section with substantial content.",
        section_id="sec_parent",
        section_title="Overview",
        section_path=["Chapter 1", "Overview"],
        section_level=2,
        parent_section_id="sec_chapter",
        token_count=180,
    )
    child_fragment = make_fragment(
        text="Specific configuration steps follow.",
        section_id="sec_child",
        section_title="Advanced Configuration",
        section_path=["Chapter 1", "Overview", "Advanced Configuration"],
        section_level=3,
        parent_section_id="sec_parent",
        token_count=10,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[parent_fragment],
        next_fragment=child_fragment,
    )

    assert should_flush is True
