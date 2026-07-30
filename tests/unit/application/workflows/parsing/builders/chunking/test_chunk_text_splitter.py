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
    ) -> dict[str, object]:
        del add_special_tokens, truncation
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
