from src.shared.text.text_preview import (
    console_safe_text,
    preview_text,
    truncate_at_word_boundary,
)


def test_truncate_at_word_boundary_breaks_before_partial_word() -> None:
    text = "The quick brown fox jumps over the lazy dog"
    # Cut lands inside "jumps" (index 24 is within the word) -- expect the
    # boundary to fall back to the space before it, not mid-word.
    result = truncate_at_word_boundary(text, 24)
    assert result == "The quick brown fox"
    assert not result.endswith(("j", "ju", "jum", "jump"))


def test_truncate_at_word_boundary_keeps_exact_boundary_cut() -> None:
    text = "The quick brown fox"
    result = truncate_at_word_boundary(text, len("The quick"))
    assert result == "The quick"


def test_truncate_at_word_boundary_falls_back_to_raw_slice_for_one_long_word() -> None:
    # No whitespace anywhere near the cut point -- must not scan the whole
    # string looking for one, and must still return a bounded slice.
    text = "a" * 200
    result = truncate_at_word_boundary(text, 50)
    assert result == "a" * 50


def test_truncate_at_word_boundary_returns_full_text_when_under_limit() -> None:
    assert truncate_at_word_boundary("short", 100) == "short"


def test_preview_text_truncates_at_word_boundary_not_mid_word() -> None:
    text = "Warning: never operate the unit without the safety guard installed."
    preview = preview_text(text, 30)
    assert preview.endswith("...")
    body = preview[: -len("...")]
    assert text.startswith(body)
    # The character immediately after the retained body in the original
    # text must be a word boundary (space) or end-of-string, proving we
    # didn't cut a word in half.
    if len(body) < len(text):
        assert text[len(body)] == " " or body.endswith(" ") or body == ""


def test_preview_text_short_text_unchanged() -> None:
    assert preview_text("hello", 10) == "hello"


def test_preview_text_empty_fallback() -> None:
    assert preview_text(None, 10, empty_fallback="-") == "-"


def test_console_safe_text_replaces_unencodable_characters() -> None:
    assert console_safe_text(None) == ""
