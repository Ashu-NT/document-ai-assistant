from src.application.workflows.parsing.builders.document_graph.chunk_statistics_builder import (
    ChunkStatisticsBuilder,
)


class _FakeTokenCounter:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def count_tokens(self, text: str | None) -> int:
        safe_text = text or ""
        self.calls.append(safe_text)
        return len(safe_text.replace(" ", ""))


def test_chunk_statistics_builder_uses_configured_token_counter() -> None:
    token_counter = _FakeTokenCounter()
    builder = ChunkStatisticsBuilder(token_counter=token_counter)

    statistics = builder.build("alpha beta")

    assert statistics.char_count == len("alpha beta")
    assert statistics.token_count_estimate == len("alphabeta")
    assert token_counter.calls == ["alpha beta"]


def test_chunk_statistics_builder_keeps_minimum_estimate_for_empty_text() -> None:
    builder = ChunkStatisticsBuilder(token_counter=_FakeTokenCounter())

    statistics = builder.build("")

    assert statistics.char_count == 0
    assert statistics.token_count_estimate == 1
