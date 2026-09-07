from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.section_chunk.chunk_fragment_packer import (
    ChunkFragmentPacker,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge.section_merge_policy import (
    SectionMergePolicy,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ChunkType


def make_fragment(
    *,
    text: str,
    token_count: int,
    order_index: int,
    list_run_id: str | None = None,
    list_run_total_tokens: int | None = None,
) -> ChunkFragment:
    return ChunkFragment(
        text=text,
        chunk_type=ChunkType.GENERAL,
        order_index=order_index,
        section_id="s1",
        section_path=["1 Intro"],
        token_count=token_count,
        list_run_id=list_run_id,
        list_run_total_tokens=list_run_total_tokens,
    )


def _pack(fragments: list[ChunkFragment]) -> list[list[str]]:
    text_splitter = ChunkTextSplitter(max_chunk_tokens=50, chunk_overlap=0)
    merge_policy = SectionMergePolicy(
        text_splitter=text_splitter,
        min_section_text_length=10,
    )
    payloads = ChunkFragmentPacker().pack(
        document_title=None,
        fragments=fragments,
        text_splitter=text_splitter,
        payload_factory=ChunkPayloadFactory(),
        merge_policy=merge_policy,
    )
    return [
        [
            fragment.text
            for fragment in fragments
            if fragment.text in payload.content
        ]
        for payload in payloads
    ]


def test_without_list_run_tagging_a_long_run_splits_arbitrarily_on_token_budget() -> (
    None
):
    # Baseline: fragments with no list_run metadata (the pre-existing
    # behavior, and still what happens for any non-LIST_ITEM content) split
    # purely once the running token total exceeds max_chunk_tokens,
    # regardless of where that lands relative to a logical unit.
    intro = make_fragment(text="Intro paragraph.", token_count=30, order_index=1)
    step_1 = make_fragment(text="Step 1.", token_count=10, order_index=2)
    step_2 = make_fragment(text="Step 2.", token_count=10, order_index=3)
    step_3 = make_fragment(text="Step 3.", token_count=10, order_index=4)

    text_splitter = ChunkTextSplitter(max_chunk_tokens=50, chunk_overlap=0)
    merge_policy = SectionMergePolicy(text_splitter=text_splitter, min_section_text_length=10)
    payloads = ChunkFragmentPacker().pack(
        document_title=None,
        fragments=[intro, step_1, step_2, step_3],
        text_splitter=text_splitter,
        payload_factory=ChunkPayloadFactory(),
        merge_policy=merge_policy,
    )

    # Intro + step 1 + step 2 = 50 tokens (fits); step 3 pushes to 60 and
    # gets split into its own chunk -- the 3-step list fractures 2/1.
    assert len(payloads) == 2
    assert "Step 3." not in payloads[0].content
    assert "Step 3." in payloads[1].content


def test_list_run_tagging_flushes_before_the_run_instead_of_splitting_it() -> None:
    intro = make_fragment(text="Intro paragraph.", token_count=30, order_index=1)
    step_1 = make_fragment(
        text="Step 1.",
        token_count=10,
        order_index=2,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=30,
    )
    step_2 = make_fragment(
        text="Step 2.",
        token_count=10,
        order_index=3,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=30,
    )
    step_3 = make_fragment(
        text="Step 3.",
        token_count=10,
        order_index=4,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=30,
    )

    groups = _pack([intro, step_1, step_2, step_3])

    assert len(groups) == 2
    assert groups[0] == ["Intro paragraph."]
    assert groups[1] == ["Step 1.", "Step 2.", "Step 3."]


def test_flushes_before_an_oversized_list_run_to_give_it_a_clean_start() -> None:
    # The list itself (70 tokens) exceeds max_chunk_tokens (50) -- splitting
    # across multiple chunks is unavoidable, but the run should still start
    # its own chunk rather than being glued to unrelated preceding content;
    # it then fractures at the fragment boundary once the running total
    # overflows, same as any other overflowing content.
    intro = make_fragment(text="Intro paragraph.", token_count=10, order_index=1)
    step_1 = make_fragment(
        text="Step 1.",
        token_count=35,
        order_index=2,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=70,
    )
    step_2 = make_fragment(
        text="Step 2.",
        token_count=35,
        order_index=3,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=70,
    )

    groups = _pack([intro, step_1, step_2])

    assert len(groups) == 3
    assert groups[0] == ["Intro paragraph."]
    assert groups[1] == ["Step 1."]
    assert groups[2] == ["Step 2."]


def test_merged_sibling_sections_keep_all_touched_section_ids_for_cross_reference_lookup() -> (
    None
):
    # Regression for the section-path collapse bug: SectionMergePolicy folds
    # "1.7 Interrupt Handling Setup" and "1.8 Interrupt Handling
    # Verification" into one chunk because they share a real title topic
    # ("interrupt handling") -- a genuine positive merge signal, not just
    # shared numbering or shared broad family (same family alone is no
    # longer sufficient -- see test_section_merge_policy.py). The
    # "1 General" intro fragment does NOT fold in with them: "General"
    # isn't recognized introductory language, so it stays its own chunk
    # (the conservative default). The merged chunk's primary section_id/
    # section_path still collapse to the common ancestor "1 General" for
    # display (same as the intro chunk's), but section_ids must list every
    # subsection so a fuzzy "see section 1.8" reference can find this
    # chunk and not the unrelated intro chunk (see ChunkSectionNumberIndex).
    general = ChunkFragment(
        text="General provisions apply to this contract.",
        chunk_type=ChunkType.GENERAL,
        order_index=1,
        section_id="s_general",
        section_title="1 General",
        section_path=["1 General"],
        section_level=1,
        parent_section_id=None,
        token_count=10,
    )
    setup = ChunkFragment(
        text="1.7 Interrupt Handling Setup configures the vector table.",
        chunk_type=ChunkType.GENERAL,
        order_index=2,
        section_id="s_17",
        section_title="1.7 Interrupt Handling Setup",
        section_path=["1 General", "1.7 Interrupt Handling Setup"],
        section_level=2,
        parent_section_id="s_general",
        token_count=8,
    )
    verification = ChunkFragment(
        text="1.8 Interrupt Handling Verification checks the ISR fires correctly.",
        chunk_type=ChunkType.GENERAL,
        order_index=3,
        section_id="s_18",
        section_title="1.8 Interrupt Handling Verification",
        section_path=["1 General", "1.8 Interrupt Handling Verification"],
        section_level=2,
        parent_section_id="s_general",
        token_count=8,
    )
    section_path_lookup = {
        ("1 General",): "s_general",
        ("1 General", "1.7 Interrupt Handling Setup"): "s_17",
        ("1 General", "1.8 Interrupt Handling Verification"): "s_18",
    }

    text_splitter = ChunkTextSplitter(max_chunk_tokens=50, chunk_overlap=0)
    merge_policy = SectionMergePolicy(
        text_splitter=text_splitter, min_section_text_length=10
    )
    payloads = ChunkFragmentPacker().pack(
        document_title=None,
        fragments=[general, setup, verification],
        section_path_lookup=section_path_lookup,
        text_splitter=text_splitter,
        payload_factory=ChunkPayloadFactory(),
        merge_policy=merge_policy,
    )

    assert len(payloads) == 2
    general_payload, merged_payload = payloads

    assert general_payload.section_ids == ["s_general"]
    assert "General provisions" in general_payload.content

    assert merged_payload.section_path == ["1 General"]
    assert merged_payload.section_ids == ["s_general", "s_17", "s_18"]
    assert "1.7 Interrupt Handling Setup" in merged_payload.content
    assert "1.8 Interrupt Handling Verification" in merged_payload.content


def test_does_not_flush_mid_run_between_fragments_of_the_same_list() -> None:
    step_1 = make_fragment(
        text="Step 1.",
        token_count=10,
        order_index=1,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=20,
    )
    step_2 = make_fragment(
        text="Step 2.",
        token_count=10,
        order_index=2,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=20,
    )

    groups = _pack([step_1, step_2])

    assert len(groups) == 1
    assert groups[0] == ["Step 1.", "Step 2."]
