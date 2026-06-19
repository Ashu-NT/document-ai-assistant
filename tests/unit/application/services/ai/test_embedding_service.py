import pytest

from src.application.services.ai import EmbeddingService
from src.shared.exceptions import InfrastructureError


class FakeEmbeddingProvider:
    def __init__(self) -> None:
        self.text_calls: list[str] = []
        self.batch_calls: list[list[str]] = []

    def embed_text(self, text: str) -> list[float]:
        self.text_calls.append(text)
        return [0.1, 0.2, 0.3]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self.batch_calls.append(texts)
        return [[float(index), float(index) + 0.1] for index, _ in enumerate(texts, start=1)]


class FailingEmbeddingProvider:
    def embed_text(self, text: str) -> list[float]:
        raise InfrastructureError("Embedding provider failed.")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        raise InfrastructureError("Embedding provider failed.")


def test_embed_text_calls_provider() -> None:
    provider = FakeEmbeddingProvider()
    service = EmbeddingService(provider)

    vector = service.embed_text("Hydraulic pump maintenance")

    assert vector == [0.1, 0.2, 0.3]
    assert provider.text_calls == ["Hydraulic pump maintenance"]


def test_embed_batch_calls_provider() -> None:
    provider = FakeEmbeddingProvider()
    service = EmbeddingService(provider)

    vectors = service.embed_batch(["first", "second"])

    assert vectors == [[1.0, 1.1], [2.0, 2.1]]
    assert provider.batch_calls == [["first", "second"]]


def test_embed_chunk_uses_embedding_text_when_present(sample_chunk) -> None:
    provider = FakeEmbeddingProvider()
    service = EmbeddingService(provider)
    sample_chunk.embedding_text = "Section: Maintenance\nReplace hydraulic filter."

    vector = service.embed_chunk(sample_chunk)

    assert vector == [0.1, 0.2, 0.3]
    assert provider.text_calls == ["Section: Maintenance\nReplace hydraulic filter."]


def test_embed_chunks_falls_back_to_chunk_content(sample_chunk) -> None:
    provider = FakeEmbeddingProvider()
    service = EmbeddingService(provider)
    sample_chunk.embedding_text = None

    vectors = service.embed_chunks([sample_chunk])

    assert vectors == [[1.0, 1.1]]
    assert provider.batch_calls == [[sample_chunk.content]]


def test_embed_text_does_not_swallow_errors() -> None:
    service = EmbeddingService(FailingEmbeddingProvider())

    with pytest.raises(InfrastructureError):
        service.embed_text("Hydraulic pump maintenance")


def test_embed_batch_does_not_swallow_errors() -> None:
    service = EmbeddingService(FailingEmbeddingProvider())

    with pytest.raises(InfrastructureError):
        service.embed_batch(["first", "second"])
