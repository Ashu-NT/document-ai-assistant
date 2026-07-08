from src.application.workflows.parsing.builders.chunking.text.tokenization import (
    ChunkTokenCounterFactory,
    TransformerChunkTokenCounter,
    WhitespaceChunkTokenCounter,
)


def test_chunk_token_counter_factory_defaults_to_whitespace() -> None:
    factory = ChunkTokenCounterFactory(provider="whitespace")

    first = factory.create()
    second = factory.create()

    assert isinstance(first, WhitespaceChunkTokenCounter)
    assert first is second


def test_chunk_token_counter_factory_caches_transformer_counter(
    monkeypatch,
) -> None:
    created: list[tuple[str, bool]] = []
    expected_counter = WhitespaceChunkTokenCounter()

    def fake_from_pretrained(
        cls,
        *,
        model_name: str,
        local_files_only: bool,
    ) -> WhitespaceChunkTokenCounter:
        created.append((model_name, local_files_only))
        return expected_counter

    monkeypatch.setattr(
        TransformerChunkTokenCounter,
        "from_pretrained",
        classmethod(fake_from_pretrained),
    )

    factory = ChunkTokenCounterFactory(
        provider="transformer",
        tokenizer_model="test-model",
        tokenizer_local_only=True,
    )

    first = factory.create()
    second = factory.create()

    assert first is expected_counter
    assert second is expected_counter
    assert created == [("test-model", True)]
