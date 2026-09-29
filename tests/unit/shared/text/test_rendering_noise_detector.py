from src.shared.text.rendering_noise_detector import is_rendering_only_noise


class TestRenderingOnlyNoiseExamples:
    def test_pure_markdown_separator_row_is_noise(self) -> None:
        assert is_rendering_only_noise("| --- | --- |") is True

    def test_dash_only_fence_is_noise(self) -> None:
        assert is_rendering_only_noise("----------------|----------------") is True

    def test_compact_pipe_dash_fence_is_noise(self) -> None:
        assert is_rendering_only_noise("|-----|-----|") is True

    def test_technical_content_with_pipes_and_units_is_not_noise(self) -> None:
        assert is_rendering_only_noise("DN25 | PN16 | 80 C") is False

    def test_bare_serial_number_is_not_noise(self) -> None:
        assert is_rendering_only_noise("8351446") is False

    def test_hyphenated_model_code_is_not_noise(self) -> None:
        assert is_rendering_only_noise("TCR12-43063") is False

    def test_hyphenated_word_is_not_noise(self) -> None:
        assert is_rendering_only_noise("pressure-temperature") is False


class TestBlankTextIsNotThisInvariantsConcern:
    def test_empty_string_is_not_classified_as_noise_here(self) -> None:
        # Blank/empty content is the no_empty_chunks invariant's job -
        # this detector must not double-count the same defect.
        assert is_rendering_only_noise("") is False

    def test_whitespace_only_is_not_classified_as_noise_here(self) -> None:
        assert is_rendering_only_noise("   \n\t  ") is False

    def test_none_is_not_classified_as_noise_here(self) -> None:
        assert is_rendering_only_noise(None) is False


class TestConservativeMixedContent:
    def test_content_mixed_with_fence_syntax_is_not_noise(self) -> None:
        assert is_rendering_only_noise("Value | --- | 42") is False


class TestUnicodeAwareness:
    def test_a_lone_cjk_character_is_not_noise(self) -> None:
        # Regression: a real corpus document (manual_fwc12) produced a
        # single-character CJK chunk ("金") that the ASCII-only alnum
        # check misclassified as noise - str.isalnum() is Unicode-aware
        # and correctly recognizes it as meaningful.
        assert is_rendering_only_noise("金") is False

    def test_accented_latin_text_is_not_noise(self) -> None:
        assert is_rendering_only_noise("Abnahmeprüfzeugnis") is False
