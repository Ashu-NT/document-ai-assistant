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


def test_merge_policy_keeps_intro_with_child_task_when_under_budget() -> None:
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
        section_title="Lab task 1: Feeding the ADC input directly to the DAC output",
        section_path=[
            "Chapter 1",
            "A first DSP project with Code Composer Studio",
            "Lab task 1: Feeding the ADC input directly to the DAC output",
        ],
        section_level=3,
        parent_section_id="sec_parent",
        token_count=80,
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[parent_fragment],
        next_fragment=child_fragment,
    )

    assert should_flush is False


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


def test_merge_policy_separates_unrelated_sibling_sections() -> None:
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


def test_merge_policy_separates_unrelated_numbered_sibling_sections() -> None:
    # Regression: is_task_like_title() treats ANY numbered heading as
    # "task-like", so two numbered siblings with no topic in common (e.g.
    # a contract's "1.7 Modifications" and "1.8 Liability and Warranty")
    # must not merge just because both happen to be numbered -- this was
    # the root cause of two unrelated legal sections landing in one chunk.
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

    assert should_flush is True


def test_merge_policy_merges_bare_numbered_siblings_with_no_topic_text() -> None:
    # Two numbered siblings with nothing left to compare once numbering is
    # stripped (e.g. plain "Step 1"/"Step 2") still merge -- the numbering
    # itself is the only signal that they belong to the same sequence, and
    # there's no real topic text to say otherwise.
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

    assert should_flush is False
