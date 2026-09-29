from src.application.workflows.parsing.builders.chunking import ChunkTextSplitter
from src.application.workflows.parsing.builders.chunking.text.tokenization import (
    TransformerChunkTokenCounter,
)


class _FakeFastTokenizer:
    def __call__(
        self,
        text: str,
        *,
        add_special_tokens: bool = False,
        return_offsets_mapping: bool = False,
        truncation: bool = False,
        verbose: bool = True,
    ) -> dict[str, object]:
        del add_special_tokens, truncation, verbose
        offsets = []
        cursor = 0
        for part in text.replace(",", " ,").split():
            start = text.index(part, cursor)
            end = start + len(part)
            offsets.append((start, end))
            cursor = end

        payload: dict[str, object] = {"input_ids": list(range(len(offsets)))}
        if return_offsets_mapping:
            payload["offset_mapping"] = offsets
        return payload

    def tokenize(self, text: str) -> list[str]:
        return text.replace(",", " ,").split()


def test_chunk_text_splitter_prefers_sentence_boundaries() -> None:
    splitter = ChunkTextSplitter(max_chunk_tokens=5, chunk_overlap=0)

    result = splitter.split(
        "Alpha beta gamma. Delta epsilon zeta. Eta theta iota."
    )

    assert result == [
        "Alpha beta gamma.",
        "Delta epsilon zeta.",
        "Eta theta iota.",
    ]


def test_chunk_text_splitter_prefers_clause_boundaries_over_raw_token_windows() -> None:
    splitter = ChunkTextSplitter(max_chunk_tokens=6, chunk_overlap=0)

    # One long compound sentence (no sentence-ending punctuation until the
    # very end), too long to keep whole -- should split before "unless"
    # rather than mid-clause at an arbitrary token count.
    result = splitter.split(
        "Do not open the valve, unless pressure has been fully released."
    )

    assert result == [
        "Do not open the valve",
        "unless pressure has been fully released.",
    ]


def test_chunk_text_splitter_adds_overlap_between_windows() -> None:
    splitter = ChunkTextSplitter(max_chunk_tokens=3, chunk_overlap=1)

    result = splitter.split("alpha beta gamma delta epsilon")

    assert result == [
        "alpha beta gamma",
        "gamma delta epsilon",
    ]


def test_chunk_text_splitter_uses_custom_token_counter_for_fallback_windows() -> None:
    splitter = ChunkTextSplitter(
        max_chunk_tokens=2,
        chunk_overlap=0,
        token_counter=TransformerChunkTokenCounter(tokenizer=_FakeFastTokenizer()),
    )

    result = splitter.split("alpha, beta gamma")

    assert result == [
        "alpha,",
        "beta gamma",
    ]


class TestOverlapNeverExceedsBudget:
    """Regression coverage for the proven production defect: overlap
    injection used to prepend `chunk_overlap` tokens onto every window
    after the first without rechecking the final token count, so a window
    already packed right up to budget would come out over it. See
    outputs/architecture/upstream_structural_quality_investigation.md.
    """

    @staticmethod
    def _assert_all_windows_within_budget(
        windows: list[str], splitter: ChunkTextSplitter
    ) -> None:
        for window in windows:
            assert splitter.count_tokens(window) <= splitter.max_chunk_tokens

    def test_a_full_configured_overlap_preserved_when_it_fits(self) -> None:
        # Short lines that never fully fill the budget on their own, so the
        # packed window ends up well under max_chunk_tokens - plenty of
        # headroom for the full configured overlap to survive intact.
        splitter = ChunkTextSplitter(max_chunk_tokens=5, chunk_overlap=1)

        text = "\n".join(["a b", "c d", "e f"])
        result = splitter.split(text)

        self._assert_all_windows_within_budget(result, splitter)
        assert len(result) == 2
        # window[1]'s own packed content is "e f" (2 tokens); headroom =
        # 5-2=3, so the full 1-token overlap fits and must be preserved.
        assert result[1] == "d e f"

    def test_b_configured_overlap_would_exceed_max_is_reduced(self) -> None:
        # Reproduces the Bauer-shaped mechanism directly: a window whose own
        # packed content is already very close to budget, where the full
        # configured overlap would push it over.
        splitter = ChunkTextSplitter(max_chunk_tokens=5, chunk_overlap=3)

        # raw-token-window fallback: windows of exactly 5 tokens each
        # (no sentence/line boundaries at all - one long unbroken run).
        result = splitter.split("a b c d e f g h i j")

        assert result[0] == "a b c d e"
        # window[1]'s own packed content ("f g h i j") is already exactly 5
        # tokens = the full budget - a naive +3 overlap would make it 8.
        # The fix must reduce (here: to zero) rather than exceed budget.
        self._assert_all_windows_within_budget(result, splitter)
        assert result[1] == "f g h i j"

    def test_c_payload_exactly_at_max_gets_zero_additional_overlap(self) -> None:
        splitter = ChunkTextSplitter(max_chunk_tokens=3, chunk_overlap=5)

        result = splitter.split("alpha beta gamma delta epsilon zeta")

        self._assert_all_windows_within_budget(result, splitter)
        # Every window here is exactly 3 tokens (raw token-window fallback,
        # no natural boundaries) - no room for any overlap at all.
        assert result == ["alpha beta gamma", "delta epsilon zeta"]

    def test_d_very_small_remaining_capacity_includes_only_safe_overlap(self) -> None:
        # window[1] has exactly 1 token of headroom before hitting budget -
        # only a 1-token overlap should be included, not the full 5.
        splitter = ChunkTextSplitter(max_chunk_tokens=6, chunk_overlap=5)

        result = splitter.split("aa bb cc dd ee ff gg")

        self._assert_all_windows_within_budget(result, splitter)
        assert result[0] == "aa bb cc dd ee ff"
        # window[1] own content is "gg" (1 token); headroom = 6-1 = 5, so
        # the full configured overlap of 5 actually DOES fit here - use a
        # tighter case below to force a genuine partial-overlap reduction.
        splitter = ChunkTextSplitter(max_chunk_tokens=6, chunk_overlap=5)
        result = splitter.split("aa bb cc dd ee ff gg hh")
        self._assert_all_windows_within_budget(result, splitter)
        # window[1] own content "gg hh" = 2 tokens; headroom = 4; configured
        # overlap 5 must be reduced to 4 (the largest amount that fits).
        assert result[1] == "cc dd ee ff gg hh"

    def test_e_multiple_consecutive_windows_all_stay_within_budget(self) -> None:
        splitter = ChunkTextSplitter(max_chunk_tokens=4, chunk_overlap=2)

        result = splitter.split(
            "one two three four five six seven eight nine ten eleven twelve"
        )

        assert len(result) > 2
        self._assert_all_windows_within_budget(result, splitter)

    def test_f_zero_overlap_behavior_unchanged(self) -> None:
        splitter = ChunkTextSplitter(max_chunk_tokens=3, chunk_overlap=0)

        result = splitter.split("alpha beta gamma delta epsilon zeta")

        assert result == ["alpha beta gamma", "delta epsilon zeta"]
        self._assert_all_windows_within_budget(result, splitter)

    def test_g_raw_token_window_fallback_invariant_holds(self) -> None:
        # No punctuation, no newlines, no clause conjunctions anywhere -
        # forces the deepest recursion level (_split_token_windows).
        splitter = ChunkTextSplitter(max_chunk_tokens=5, chunk_overlap=4)

        result = splitter.split(
            "wordone wordtwo wordthree wordfour wordfive wordsix wordseven "
            "wordeight wordnine wordten"
        )

        self._assert_all_windows_within_budget(result, splitter)
        assert len(result) >= 2

    def test_h_line_level_splitting_invariant_holds(self) -> None:
        # Mirrors the real Bauer/Deck-Fillers shape: multiple short lines,
        # none individually oversized, packed greedily up to budget.
        splitter = ChunkTextSplitter(max_chunk_tokens=6, chunk_overlap=3)

        text = "\n".join(
            [
                "line one two",
                "line three four",
                "line five six",
                "line seven eight",
            ]
        )
        result = splitter.split(text)

        self._assert_all_windows_within_budget(result, splitter)

    def test_i_sentence_and_clause_splitting_invariant_holds(self) -> None:
        splitter = ChunkTextSplitter(max_chunk_tokens=6, chunk_overlap=3)

        result = splitter.split(
            "Do not open the valve, unless pressure has been fully released. "
            "Check the gauge before proceeding."
        )

        self._assert_all_windows_within_budget(result, splitter)

    def test_j_reducing_overlap_never_removes_the_non_overlap_payload(self) -> None:
        splitter = ChunkTextSplitter(max_chunk_tokens=5, chunk_overlap=3)

        result = splitter.split("a b c d e f g h i j")

        # window[1]'s own packed content ("f g h i j") must survive intact
        # even when overlap is reduced to zero to respect budget.
        assert result[1].endswith("f g h i j")

    def test_k_deterministic_output_across_repeated_runs(self) -> None:
        splitter = ChunkTextSplitter(max_chunk_tokens=5, chunk_overlap=3)
        text = "a b c d e f g h i j k l m"

        first = splitter.split(text)
        second = splitter.split(text)

        assert first == second

    def test_l_existing_valid_overlap_behavior_still_works(self) -> None:
        # Same as the pre-existing splitter test - full overlap fits
        # comfortably, so behavior must be identical to before the fix.
        splitter = ChunkTextSplitter(max_chunk_tokens=3, chunk_overlap=1)

        result = splitter.split("alpha beta gamma delta epsilon")

        assert result == [
            "alpha beta gamma",
            "gamma delta epsilon",
        ]


class TestOverlapBudgetRegressionRealProfiles:
    """Synthetic reproductions of the two real documented mechanisms,
    using the exact profile max_chunk_tokens/chunk_overlap values, without
    requiring the real PDFs or a real Docling parse."""

    def test_manual_profile_shaped_overshoot_is_fixed(self) -> None:
        # manual.yaml: max_chunk_tokens=310, chunk_overlap=20. Reproduces
        # the Bauer mechanism: a packed window whose own content (300
        # tokens) plus the full configured overlap (20) would land at
        # exactly the previously-observed defective value of 320.
        splitter = ChunkTextSplitter(max_chunk_tokens=310, chunk_overlap=20)
        window_zero_words = ["w"] * 290
        window_one_words = ["w"] * 300
        text = " ".join(window_zero_words) + "\n" + " ".join(window_one_words)

        result = splitter.split(text)

        for window in result:
            assert splitter.count_tokens(window) <= 310

    def test_datasheet_profile_shaped_overshoot_is_fixed(self) -> None:
        # datasheet.yaml: max_chunk_tokens=270, chunk_overlap=75. Reproduces
        # the Deck Fillers mechanism: a packed window whose own content
        # (254 tokens) plus the full configured overlap (75) would land at
        # the previously-observed defective value of 329.
        splitter = ChunkTextSplitter(max_chunk_tokens=270, chunk_overlap=75)
        window_zero_words = ["w"] * 157
        window_one_words = ["w"] * 254
        text = " ".join(window_zero_words) + "\n" + " ".join(window_one_words)

        result = splitter.split(text)

        for window in result:
            assert splitter.count_tokens(window) <= 270
