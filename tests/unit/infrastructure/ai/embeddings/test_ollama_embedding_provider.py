import sys
import types

import pytest

from src.infrastructure.ai.embeddings.ollama_embedding_provider import (
    OllamaEmbeddingProvider,
)
from src.shared.exceptions import InfrastructureError


class _FakeEmbedResponse(dict):
    """Mimics ollama's SubscriptableBaseModel response (dict-style access)."""


def _install_fake_ollama_module(monkeypatch, *, embed=None, embeddings=None):
    fake_module = types.SimpleNamespace()
    if embed is not None:
        fake_module.embed = embed
    if embeddings is not None:
        fake_module.embeddings = embeddings
    monkeypatch.setitem(sys.modules, "ollama", fake_module)


def test_embed_batch_sends_one_batched_request_instead_of_one_per_text(
    monkeypatch,
) -> None:
    calls = []

    def fake_embed(*, model, input):
        calls.append({"model": model, "input": list(input)})
        return _FakeEmbedResponse(
            embeddings=[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        )

    _install_fake_ollama_module(monkeypatch, embed=fake_embed)
    provider = OllamaEmbeddingProvider(model_name="nomic-embed-text")

    result = provider.embed_batch(["one", "two", "three"])

    assert len(calls) == 1
    assert calls[0]["input"] == ["one", "two", "three"]
    assert result == [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]


def test_embed_batch_wraps_underlying_errors(monkeypatch) -> None:
    def failing_embed(*, model, input):
        raise RuntimeError("ollama unreachable")

    _install_fake_ollama_module(monkeypatch, embed=failing_embed)
    provider = OllamaEmbeddingProvider(model_name="nomic-embed-text")

    with pytest.raises(InfrastructureError):
        provider.embed_batch(["one", "two"])


def test_embed_batch_raises_when_ollama_package_missing(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "ollama", None)
    provider = OllamaEmbeddingProvider(model_name="nomic-embed-text")

    with pytest.raises(InfrastructureError):
        provider.embed_batch(["one"])
