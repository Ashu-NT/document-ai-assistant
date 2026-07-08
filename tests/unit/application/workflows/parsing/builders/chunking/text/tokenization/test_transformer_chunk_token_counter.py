import re

from src.application.workflows.parsing.builders.chunking.text.tokenization import (
    TransformerChunkTokenCounter,
)


class FakeFastTokenizer:
    def __call__(
        self,
        text: str,
        *,
        add_special_tokens: bool = False,
        return_offsets_mapping: bool = False,
        truncation: bool = False,
    ) -> dict[str, object]:
        del add_special_tokens, truncation
        offsets = [
            (match.start(), match.end())
            for match in re.finditer(r"[A-Za-z]+|[.,!?]", text)
        ]
        payload: dict[str, object] = {"input_ids": list(range(len(offsets)))}
        if return_offsets_mapping:
            payload["offset_mapping"] = offsets
        return payload

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"[A-Za-z]+|[.,!?]", text)


class FakeTokenizerWithoutOffsets:
    def __call__(
        self,
        text: str,
        *,
        add_special_tokens: bool = False,
        return_offsets_mapping: bool = False,
        truncation: bool = False,
    ) -> dict[str, object]:
        del text, add_special_tokens, return_offsets_mapping, truncation
        return {"input_ids": [0, 1, 2]}

    def tokenize(self, text: str) -> list[str]:
        return text.split()


def test_transformer_chunk_token_counter_counts_tokens_from_offsets() -> None:
    counter = TransformerChunkTokenCounter(tokenizer=FakeFastTokenizer())

    assert counter.count_tokens("alpha, beta gamma") == 4


def test_transformer_chunk_token_counter_truncates_with_offsets() -> None:
    counter = TransformerChunkTokenCounter(tokenizer=FakeFastTokenizer())

    assert counter.truncate_to_tokens("alpha, beta gamma", 2) == "alpha,"


def test_transformer_chunk_token_counter_returns_tail_text_from_offsets() -> None:
    counter = TransformerChunkTokenCounter(tokenizer=FakeFastTokenizer())

    assert counter.tail_text("alpha, beta gamma", 2) == "beta gamma"


def test_transformer_chunk_token_counter_splits_windows_with_offsets() -> None:
    counter = TransformerChunkTokenCounter(tokenizer=FakeFastTokenizer())

    assert counter.split_token_windows("alpha, beta gamma", 2) == [
        "alpha,",
        "beta gamma",
    ]


def test_transformer_chunk_token_counter_falls_back_when_offsets_missing() -> None:
    counter = TransformerChunkTokenCounter(tokenizer=FakeTokenizerWithoutOffsets())

    assert counter.count_tokens("alpha beta gamma") == 3
    assert counter.truncate_to_tokens("alpha beta gamma", 2) == "alpha beta"
