from src.application.workflows.parsing.builders.chunking import ChunkTextSplitter


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


def test_chunk_text_splitter_adds_overlap_between_windows() -> None:
    splitter = ChunkTextSplitter(max_chunk_tokens=3, chunk_overlap=1)

    result = splitter.split("alpha beta gamma delta epsilon")

    assert result == [
        "alpha beta gamma",
        "gamma delta epsilon",
    ]
