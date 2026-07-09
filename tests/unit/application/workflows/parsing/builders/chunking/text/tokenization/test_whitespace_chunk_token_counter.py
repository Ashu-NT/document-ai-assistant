from src.application.workflows.parsing.builders.chunking.text.tokenization import (
    WhitespaceChunkTokenCounter,
)


def test_whitespace_chunk_token_counter_counts_tokens() -> None:
    counter = WhitespaceChunkTokenCounter()

    assert counter.count_tokens("alpha beta gamma") == 3
    assert counter.count_tokens("") == 0
    assert counter.count_tokens(None) == 0


def test_whitespace_chunk_token_counter_returns_tail_text() -> None:
    counter = WhitespaceChunkTokenCounter()

    assert counter.tail_text("alpha beta gamma delta", 2) == "gamma delta"
    assert counter.tail_text("alpha beta", 0) == ""


def test_whitespace_chunk_token_counter_truncates_to_tokens() -> None:
    counter = WhitespaceChunkTokenCounter()

    assert counter.truncate_to_tokens("alpha beta gamma", 2) == "alpha beta"
    assert counter.truncate_to_tokens("alpha beta", 5) == "alpha beta"


def test_whitespace_chunk_token_counter_truncates_with_count() -> None:
    counter = WhitespaceChunkTokenCounter()

    assert counter.truncate_to_tokens_with_count("alpha beta gamma", 2) == (
        "alpha beta",
        2,
    )
    assert counter.truncate_to_tokens_with_count("alpha beta", 5) == (
        "alpha beta",
        2,
    )
    assert counter.truncate_to_tokens_with_count("alpha beta", 0) == ("", 0)


def test_whitespace_chunk_token_counter_splits_windows() -> None:
    counter = WhitespaceChunkTokenCounter()

    assert counter.split_token_windows("alpha beta gamma delta epsilon", 2) == [
        "alpha beta",
        "gamma delta",
        "epsilon",
    ]
