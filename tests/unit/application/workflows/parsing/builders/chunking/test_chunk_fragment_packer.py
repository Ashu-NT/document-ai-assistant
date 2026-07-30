from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.section_chunk.chunk_fragment_packer import (
    ChunkFragmentPacker,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge_policy import (
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


def test_does_not_flush_before_a_list_run_that_would_not_fit_in_one_chunk_anyway() -> (
    None
):
    # The list itself (70 tokens) exceeds max_chunk_tokens (50) -- no
    # proactive flush can help, splitting remains unavoidable, and the
    # packer must fall through to its normal overflow handling rather than
    # flushing pointlessly before every fragment of an oversized run.
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

    assert len(groups) == 2
    assert groups[0] == ["Intro paragraph.", "Step 1."]
    assert groups[1] == ["Step 2."]


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
