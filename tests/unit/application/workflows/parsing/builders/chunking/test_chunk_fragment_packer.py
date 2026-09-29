import re

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


def _pad_to_real_token_count(text: str, token_count: int) -> str:
    """Pads `text` with filler words so its REAL whitespace-token count
    equals `token_count`, keeping `text` itself as a findable prefix.

    Since the packer now validates budgets against the real re-tokenized
    serialized text (see ChunkFragmentPacker._fits_budget) rather than a
    per-fragment additive estimate, every fixture's declared `token_count`
    must match what a real tokenizer would count for its actual text -
    otherwise these fragments would silently be lying about their own
    size, exactly the class of bug the production fix addresses.
    """
    real_count = len(text.split())
    filler_needed = max(0, token_count - real_count)
    if not filler_needed:
        return text
    filler = " ".join(f"filler{i}" for i in range(filler_needed))
    return f"{text} {filler}"


def make_fragment(
    *,
    text: str,
    token_count: int,
    order_index: int,
    list_run_id: str | None = None,
    list_run_total_tokens: int | None = None,
    docling_group_id: str | None = None,
    docling_group_type: str | None = None,
    docling_group_total_tokens: int | None = None,
) -> ChunkFragment:
    return ChunkFragment(
        text=_pad_to_real_token_count(text, token_count),
        chunk_type=ChunkType.GENERAL,
        order_index=order_index,
        section_id="s1",
        section_path=["1 Intro"],
        token_count=token_count,
        list_run_id=list_run_id,
        list_run_total_tokens=list_run_total_tokens,
        docling_group_id=docling_group_id,
        docling_group_type=docling_group_type,
        docling_group_total_tokens=docling_group_total_tokens,
    )


def _strip_filler(text: str) -> str:
    """Inverse of `_pad_to_real_token_count` - recovers the original,
    readable label for test assertions (the padded filler words are only
    there to make the fragment's declared `token_count` match what a real
    tokenizer counts; they are not part of the label under test)."""
    return re.sub(r"(\s+filler\d+)+$", "", text)


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
            _strip_filler(fragment.text)
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


def test_without_group_tagging_a_small_key_value_group_splits_arbitrarily_and_absorbs_filler() -> (
    None
):
    """Baseline ("before"): reproduces the real Kliewe-datasheet pattern
    (a ~13-token key_value_area group scattered across chunks despite
    fitting comfortably under budget) using synthetic fragments -- no
    Docling group metadata, matching pre-fix behavior for every fragment
    type today. Companion to the "after" test below."""
    filler = make_fragment(text="Unrelated paragraph.", token_count=30, order_index=1)
    kv_1 = make_fragment(text="Nr.:", token_count=8, order_index=2)
    kv_2 = make_fragment(text="FB-8.6-21", token_count=8, order_index=3)
    kv_3 = make_fragment(text="Seite: 1 von 1", token_count=8, order_index=4)

    groups = _pack([filler, kv_1, kv_2, kv_3])

    # 30 + 8 + 8 = 46 fits, so kv_1/kv_2 get glued to the unrelated filler;
    # kv_3 then pushes the running total to 54, overflowing the 50-token
    # budget -- the group fractures 2/1 across chunks, with no protection
    # keeping its 3 members (24 tokens total) together despite comfortably
    # fitting the budget on their own.
    assert len(groups) == 2
    assert groups[0] == ["Unrelated paragraph.", "Nr.:", "FB-8.6-21"]
    assert groups[1] == ["Seite: 1 von 1"]


def test_key_value_group_cohesion_flushes_filler_and_keeps_the_whole_group_together() -> (
    None
):
    """Regression fixture for the real Kliewe-datasheet fragmentation
    pattern ("after" the fix): a small key_value_area group that would
    otherwise get glued to unrelated preceding content (or split) now
    gets its own clean chunk, and the unrelated neighbor is flushed out
    on its own -- it never becomes part of the group's chunk."""
    filler = make_fragment(text="Unrelated paragraph.", token_count=30, order_index=1)
    kv_1 = make_fragment(
        text="Nr.:",
        token_count=8,
        order_index=2,
        docling_group_id="#/groups/0",
        docling_group_type="key_value_area",
        docling_group_total_tokens=24,
    )
    kv_2 = make_fragment(
        text="FB-8.6-21",
        token_count=8,
        order_index=3,
        docling_group_id="#/groups/0",
        docling_group_type="key_value_area",
        docling_group_total_tokens=24,
    )
    kv_3 = make_fragment(
        text="Seite: 1 von 1",
        token_count=8,
        order_index=4,
        docling_group_id="#/groups/0",
        docling_group_type="key_value_area",
        docling_group_total_tokens=24,
    )

    groups = _pack([filler, kv_1, kv_2, kv_3])

    assert len(groups) == 2
    assert groups[0] == ["Unrelated paragraph."]
    assert groups[1] == ["Nr.:", "FB-8.6-21", "Seite: 1 von 1"]


def test_flushes_before_an_oversized_key_value_group_but_still_allows_it_to_split() -> (
    None
):
    # The group itself (70 tokens) exceeds max_chunk_tokens (50) -- the
    # hard budget constraint must win: splitting across multiple chunks
    # stays allowed, cohesion never overrides it. The group still starts
    # its own clean chunk rather than gluing to unrelated preceding
    # content, exactly mirroring the oversized-list-run case above.
    intro = make_fragment(text="Intro paragraph.", token_count=10, order_index=1)
    kv_1 = make_fragment(
        text="Field 1.",
        token_count=35,
        order_index=2,
        docling_group_id="#/groups/0",
        docling_group_type="key_value_area",
        docling_group_total_tokens=70,
    )
    kv_2 = make_fragment(
        text="Field 2.",
        token_count=35,
        order_index=3,
        docling_group_id="#/groups/0",
        docling_group_type="key_value_area",
        docling_group_total_tokens=70,
    )

    groups = _pack([intro, kv_1, kv_2])

    assert len(groups) == 3
    assert groups[0] == ["Intro paragraph."]
    assert groups[1] == ["Field 1."]
    assert groups[2] == ["Field 2."]


class TestRenderingOnlyNoiseWindowsAreDropped:
    """Defensive backstop for the degraded-table fallback path: if a
    standalone oversized fragment's text still somehow contains pure
    table-rendering syntax (e.g. because it came from some other, untouched
    code path), the generic-splitter fallback must never emit a final
    chunk consisting of nothing else - while never discarding a window
    that has any real meaningful content, even if it also contains fence
    syntax. See src/shared/text/rendering_noise_detector.py."""

    def _pack_standalone(self, fragment: ChunkFragment) -> list[str]:
        text_splitter = ChunkTextSplitter(max_chunk_tokens=5, chunk_overlap=0)
        merge_policy = SectionMergePolicy(text_splitter=text_splitter, min_section_text_length=10)
        payloads = ChunkFragmentPacker().pack(
            document_title=None,
            fragments=[fragment],
            text_splitter=text_splitter,
            payload_factory=ChunkPayloadFactory(),
            merge_policy=merge_policy,
        )
        return [payload.content for payload in payloads]

    def test_pure_fence_window_is_dropped_but_meaningful_windows_survive(self) -> None:
        fragment = ChunkFragment(
            text="engine no 8351446 turbocharger TCR12-43063\n"
            "--------- --------- --------- ---------\n"
            "12V175D-ML pressure 995 mbar",
            chunk_type=ChunkType.GENERAL,
            standalone=True,
            order_index=1,
            section_id="s1",
            section_path=["1 Intro"],
            token_count=20,
        )

        contents = self._pack_standalone(fragment)

        joined = " ".join(contents)
        assert "8351446" in joined
        assert "TCR12-43063" in joined
        assert "12V175D-ML" in joined
        assert not any(
            content.strip() and content.replace("-", "").strip() == ""
            for content in contents
        )

    def test_meaningful_content_alone_is_never_dropped(self) -> None:
        fragment = ChunkFragment(
            text="DN25 PN16 80 C TCR12-43063 pressure-temperature 8351446 measurement data",
            chunk_type=ChunkType.GENERAL,
            standalone=True,
            order_index=1,
            section_id="s1",
            section_path=["1 Intro"],
            token_count=20,
        )

        contents = self._pack_standalone(fragment)

        joined = " ".join(contents)
        for value in ("DN25", "PN16", "TCR12-43063", "8351446"):
            assert value in joined


def test_list_run_and_key_value_group_cohesion_operate_independently() -> None:
    """Regression: the new key_value_area cohesion check must not alter
    pre-existing list-run flush behavior, and vice versa -- each
    protection fires cleanly for its own kind of fragment in the same
    packing pass with no cross-interference."""
    step_1 = make_fragment(
        text="Step 1.",
        token_count=12,
        order_index=1,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=36,
    )
    step_2 = make_fragment(
        text="Step 2.",
        token_count=12,
        order_index=2,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=36,
    )
    step_3 = make_fragment(
        text="Step 3.",
        token_count=12,
        order_index=3,
        list_run_id="s1::list_run_1",
        list_run_total_tokens=36,
    )
    kv_1 = make_fragment(
        text="Nr.:",
        token_count=10,
        order_index=4,
        docling_group_id="#/groups/0",
        docling_group_type="key_value_area",
        docling_group_total_tokens=20,
    )
    kv_2 = make_fragment(
        text="FB-8.6-21",
        token_count=10,
        order_index=5,
        docling_group_id="#/groups/0",
        docling_group_type="key_value_area",
        docling_group_total_tokens=20,
    )

    groups = _pack([step_1, step_2, step_3, kv_1, kv_2])

    # List run (36 tokens) packs cleanly on its own; adding the key_value
    # group (20 more) would overflow 50, so it flushes before kv_1 starts
    # and gets its own clean chunk too.
    assert len(groups) == 2
    assert groups[0] == ["Step 1.", "Step 2.", "Step 3."]
    assert groups[1] == ["Nr.:", "FB-8.6-21"]


def _words(label: str, count: int) -> str:
    """Real, distinct whitespace-tokens - `count` words long, starting
    with `label` so it stays a findable marker in assembled content."""
    if count <= 1:
        return label
    return label + " " + " ".join(f"{label}_w{i}" for i in range(count - 1))


def _real_fragment(
    *,
    text: str,
    order_index: int,
    section_path: list[str],
    section_title: str | None = None,
    section_id: str = "s1",
    page_start: int | None = None,
    page_end: int | None = None,
    element_ids: list[str] | None = None,
    table_ids: list[str] | None = None,
    picture_ids: list[str] | None = None,
    chunk_type: ChunkType = ChunkType.GENERAL,
) -> ChunkFragment:
    """Builds a fragment whose declared `token_count` is ALWAYS the real
    whitespace-token count of its own text alone - i.e. never lying about
    its own size, the precondition the production fix assumes holds for
    every individual fragment (only the MULTI-fragment assembled text can
    legitimately differ, due to inserted section titles)."""
    return ChunkFragment(
        text=text,
        chunk_type=chunk_type,
        order_index=order_index,
        section_id=section_id,
        section_title=section_title,
        section_path=section_path,
        token_count=len(text.split()),
        page_start=page_start,
        page_end=page_end,
        element_ids=element_ids or [],
        table_ids=table_ids or [],
        picture_ids=picture_ids or [],
    )


def _real_pack(fragments: list[ChunkFragment], *, max_chunk_tokens: int = 50):
    text_splitter = ChunkTextSplitter(max_chunk_tokens=max_chunk_tokens, chunk_overlap=0)
    merge_policy = SectionMergePolicy(text_splitter=text_splitter, min_section_text_length=1)
    return ChunkFragmentPacker().pack(
        document_title=None,
        fragments=fragments,
        text_splitter=text_splitter,
        payload_factory=ChunkPayloadFactory(),
        merge_policy=merge_policy,
    ), text_splitter


class TestExactSerializedBudgetIsAuthoritative:
    """Regression coverage for the proven MTU production defect: the
    packer used to accept a candidate pack whenever the SUM of each
    fragment's own pre-computed token_count stayed under budget, even
    though the real assembled-and-cleaned payload text (which can include
    an inserted `section_title` when packed fragments span more than one
    section - see ChunkPayloadFactory._assemble_chunk_content) sometimes
    tokenizes to more than that sum. See
    outputs/architecture/mtu_challenge_document_reconnaissance.md and the
    hard-token-budget-correction report."""

    def test_additive_estimate_under_budget_but_real_serialization_over_budget_splits(
        self,
    ) -> None:
        # Additive sum: 20 + 25 = 45 <= 50 (the OLD check would have
        # accepted this). Real assembled text: 20 words + a 6-word
        # inserted section_title (since fragment B's section_path differs
        # from A's) + 25 words = 51 words > 50 - the exact MTU mechanism,
        # reproduced deterministically.
        fragment_a = _real_fragment(
            text=_words("alpha", 20),
            order_index=1,
            section_path=["1 General"],
        )
        fragment_b = _real_fragment(
            text=_words("bravo", 25),
            order_index=2,
            section_path=["1 General", "1.2 Something"],
            section_title=_words("SectionTitle", 6),
        )

        payloads, text_splitter = _real_pack([fragment_a, fragment_b])

        assert len(payloads) == 2, (
            "additive sum (45) fit, but the real serialized text (51 "
            "words, including the inserted section title) must not - "
            "these must land in separate chunks"
        )
        assert "alpha" in payloads[0].content
        assert "bravo" not in payloads[0].content
        assert "bravo" in payloads[1].content
        for payload in payloads:
            assert text_splitter.count_tokens(payload.content) <= 50

    def test_exact_joined_payload_at_budget_is_accepted(self) -> None:
        fragment_a = _real_fragment(
            text=_words("alpha", 25), order_index=1, section_path=["1 General"]
        )
        fragment_b = _real_fragment(
            text=_words("bravo", 25), order_index=2, section_path=["1 General"]
        )

        payloads, text_splitter = _real_pack([fragment_a, fragment_b])

        assert len(payloads) == 1
        assert text_splitter.count_tokens(payloads[0].content) == 50

    def test_exact_joined_payload_one_token_over_budget_is_rejected(self) -> None:
        fragment_a = _real_fragment(
            text=_words("alpha", 25), order_index=1, section_path=["1 General"]
        )
        fragment_b = _real_fragment(
            text=_words("bravo", 26), order_index=2, section_path=["1 General"]
        )

        payloads, text_splitter = _real_pack([fragment_a, fragment_b])

        assert len(payloads) == 2
        for payload in payloads:
            assert text_splitter.count_tokens(payload.content) <= 50

    def test_flush_before_overflow_preserves_prior_content_exactly(self) -> None:
        fragment_a = _real_fragment(
            text=_words("alpha", 30), order_index=1, section_path=["1 General"]
        )
        fragment_b = _real_fragment(
            text=_words("bravo", 30), order_index=2, section_path=["1 General"]
        )

        payloads, _ = _real_pack([fragment_a, fragment_b])

        assert payloads[0].content == _words("alpha", 30)

    def test_next_fragment_begins_a_new_pack_correctly(self) -> None:
        fragment_a = _real_fragment(
            text=_words("alpha", 30), order_index=1, section_path=["1 General"]
        )
        fragment_b = _real_fragment(
            text=_words("bravo", 30), order_index=2, section_path=["1 General"]
        )

        payloads, _ = _real_pack([fragment_a, fragment_b])

        assert len(payloads) == 2
        assert payloads[1].content == _words("bravo", 30)

    def test_multiple_sequential_flushes_produce_one_chunk_per_fragment(self) -> None:
        fragments = [
            _real_fragment(
                text=_words(f"frag{i}", 40), order_index=i, section_path=["1 General"]
            )
            for i in range(5)
        ]

        payloads, text_splitter = _real_pack(fragments)

        assert len(payloads) == 5
        for payload in payloads:
            assert text_splitter.count_tokens(payload.content) <= 50

    def test_no_empty_chunks_introduced(self) -> None:
        fragments = [
            _real_fragment(
                text=_words(f"frag{i}", 10), order_index=i, section_path=["1 General"]
            )
            for i in range(9)
        ]

        payloads, _ = _real_pack(fragments)

        assert all(payload.content.strip() for payload in payloads)

    def test_ordering_preserved(self) -> None:
        fragments = [
            _real_fragment(
                text=_words(f"frag{i}", 30), order_index=i, section_path=["1 General"]
            )
            for i in range(4)
        ]

        payloads, _ = _real_pack(fragments)

        markers_in_order = [
            next(i for i in range(4) if f"frag{i}" in payload.content)
            for payload in payloads
        ]
        assert markers_in_order == sorted(markers_in_order)

    def test_provenance_page_start_end_preserved(self) -> None:
        fragment_a = _real_fragment(
            text=_words("alpha", 10),
            order_index=1,
            section_path=["1 General"],
            page_start=5,
            page_end=5,
        )
        fragment_b = _real_fragment(
            text=_words("bravo", 10),
            order_index=2,
            section_path=["1 General"],
            page_start=6,
            page_end=7,
        )

        payloads, _ = _real_pack([fragment_a, fragment_b])

        assert len(payloads) == 1
        assert payloads[0].page_start == 5
        assert payloads[0].page_end == 7

    def test_section_association_preserved(self) -> None:
        fragment_a = _real_fragment(
            text=_words("alpha", 10),
            order_index=1,
            section_path=["1 General"],
            section_id="sec_general",
        )
        fragment_b = _real_fragment(
            text=_words("bravo", 40),
            order_index=2,
            section_path=["1 General"],
            section_id="sec_general",
        )

        payloads, _ = _real_pack([fragment_a, fragment_b])

        assert payloads[0].section_id == "sec_general"
        assert payloads[0].section_path == ["1 General"]

    def test_fragment_metadata_table_and_picture_ids_preserved(self) -> None:
        fragment_a = _real_fragment(
            text=_words("alpha", 10),
            order_index=1,
            section_path=["1 General"],
            element_ids=["el_1"],
            picture_ids=["pic_1"],
        )
        fragment_b = _real_fragment(
            text=_words("bravo", 10),
            order_index=2,
            section_path=["1 General"],
            element_ids=["el_2"],
        )

        payloads, _ = _real_pack([fragment_a, fragment_b])

        assert len(payloads) == 1
        assert payloads[0].element_ids == ["el_1", "el_2"]
        assert payloads[0].picture_ids == ["pic_1"]

    def test_table_fragment_still_routes_through_existing_split_path_unchanged(
        self,
    ) -> None:
        table_fragment = ChunkFragment(
            text="| A | B |\n| --- | --- |\n| 1 | 2 |",
            chunk_type=ChunkType.GENERAL,
            standalone=True,
            order_index=1,
            section_id="s1",
            section_path=["1 General"],
            token_count=8,
            table_rows=[["A", "B"], ["1", "2"]],
            table_row_start=None,
            table_row_end=None,
        )

        payloads, _ = _real_pack([table_fragment])

        # Still isolated into its own chunk via the standalone path,
        # never merged with anything - untouched by this fix.
        assert len(payloads) == 1
        assert "A" in payloads[0].content and "B" in payloads[0].content

    def test_single_fragment_over_budget_follows_existing_split_contract(self) -> None:
        oversized = _real_fragment(
            text=_words("alpha", 80), order_index=1, section_path=["1 General"]
        )

        payloads, text_splitter = _real_pack([oversized])

        # Routed to the real recursive text splitter (already
        # overlap-safe, per the prior fix), never emitted as one
        # single 80-token hard violation.
        assert len(payloads) >= 2
        for payload in payloads:
            assert text_splitter.count_tokens(payload.content) <= 50

    def test_configured_overlap_trim_loop_still_respects_exact_budget(self) -> None:
        text_splitter = ChunkTextSplitter(max_chunk_tokens=50, chunk_overlap=10)
        merge_policy = SectionMergePolicy(text_splitter=text_splitter, min_section_text_length=1)
        fragments = [
            _real_fragment(
                text=_words(f"frag{i}", 20), order_index=i, section_path=["1 General"]
            )
            for i in range(4)
        ]

        payloads = ChunkFragmentPacker().pack(
            document_title=None,
            fragments=fragments,
            text_splitter=text_splitter,
            payload_factory=ChunkPayloadFactory(),
            merge_policy=merge_policy,
        )

        for payload in payloads:
            assert text_splitter.count_tokens(payload.content) <= 50

    def test_unicode_multilingual_text_budget_check_is_accurate(self) -> None:
        fragment_a = _real_fragment(
            text=_words("Prüfung_Öl_Über", 25),
            order_index=1,
            section_path=["1 Allgemein"],
        )
        fragment_b = _real_fragment(
            text=_words("检查_压力_传感器", 25),
            order_index=2,
            section_path=["1 Allgemein"],
        )

        payloads, text_splitter = _real_pack([fragment_a, fragment_b])

        assert len(payloads) == 1
        assert text_splitter.count_tokens(payloads[0].content) == 50

    def test_many_small_fragment_packing_reproduces_mtu_shape(self) -> None:
        # ~30 tiny fragments (2-3 words each, like numbered component-
        # callout list items) spanning two sections partway through -
        # the real MTU pattern (17-34 merged fragments per chunk, a
        # section boundary crossed mid-pack).
        fragments = []
        for i in range(15):
            fragments.append(
                _real_fragment(
                    text=f"{i} Component label",
                    order_index=i,
                    section_path=["8 Instructions", "8.6 Fuel System"],
                )
            )
        for i in range(15, 30):
            fragments.append(
                _real_fragment(
                    text=f"{i} Component label",
                    order_index=i,
                    section_path=["8 Instructions", "8.7 Control Equipment"],
                    section_title=_words("LongSubsectionTitle", 8),
                )
            )

        payloads, text_splitter = _real_pack(fragments, max_chunk_tokens=50)

        assert payloads, "expected at least one payload"
        for payload in payloads:
            assert payload.content.strip()
            assert text_splitter.count_tokens(payload.content) <= 50

    def test_all_emitted_splittable_chunks_retokenize_within_budget(self) -> None:
        # Broad mixed-size property check across a varied fixture set.
        fragments = [
            _real_fragment(text=_words("a", 5), order_index=0, section_path=["1 S1"]),
            _real_fragment(text=_words("b", 45), order_index=1, section_path=["1 S1"]),
            _real_fragment(
                text=_words("c", 12),
                order_index=2,
                section_path=["1 S1", "1.1 Sub"],
                section_title=_words("Title", 7),
            ),
            _real_fragment(text=_words("d", 33), order_index=3, section_path=["1 S1", "1.1 Sub"]),
            _real_fragment(text=_words("e", 90), order_index=4, section_path=["2 S2"]),
            _real_fragment(text=_words("f", 8), order_index=5, section_path=["2 S2"]),
        ]

        payloads, text_splitter = _real_pack(fragments, max_chunk_tokens=50)

        assert payloads
        for payload in payloads:
            assert text_splitter.count_tokens(payload.content) <= 50
