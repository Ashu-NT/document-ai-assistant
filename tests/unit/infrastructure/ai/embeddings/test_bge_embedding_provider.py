import sys
import types

import pytest

from src.infrastructure.ai.embeddings import BgeEmbeddingProvider
from src.shared.exceptions import InfrastructureError


class FakeArray:
    def __init__(self, value) -> None:
        self.value = value

    def tolist(self):
        return self.value


class FakeSentenceTransformer:
    def __init__(self) -> None:
        self.calls = []

    def encode(self, inputs, **kwargs):
        self.calls.append(
            {
                "inputs": inputs,
                "kwargs": kwargs,
            }
        )

        if isinstance(inputs, list):
            return FakeArray([[0.1, 0.2], [0.3, 0.4]])

        return FakeArray([0.1, 0.2, 0.3])


class FailingSentenceTransformer:
    def encode(self, inputs, **kwargs):
        raise RuntimeError("embedding failed")


class LoaderSentenceTransformer:
    calls = []
    fail_local_only = False

    def __init__(self, model_name, **kwargs) -> None:
        LoaderSentenceTransformer.calls.append(
            {
                "model_name": model_name,
                "kwargs": kwargs,
            }
        )
        if kwargs.get("local_files_only") and LoaderSentenceTransformer.fail_local_only:
            raise RuntimeError("local cache missing")

    def encode(self, inputs, **kwargs):
        return FakeArray([0.1, 0.2, 0.3])


def test_embed_text_calls_sentence_transformer() -> None:
    model = FakeSentenceTransformer()
    provider = BgeEmbeddingProvider(
        model_name="BAAI/bge-small-en-v1.5",
        model=model,
    )

    vector = provider.embed_text("Hydraulic pump maintenance")

    assert vector == [0.1, 0.2, 0.3]
    assert model.calls == [
        {
            "inputs": "Hydraulic pump maintenance",
            "kwargs": {
                "convert_to_numpy": True,
                "normalize_embeddings": True,
                "show_progress_bar": False,
            },
        }
    ]


def test_embed_batch_calls_sentence_transformer() -> None:
    model = FakeSentenceTransformer()
    provider = BgeEmbeddingProvider(
        model_name="BAAI/bge-small-en-v1.5",
        model=model,
    )

    vectors = provider.embed_batch(["first", "second"])

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert model.calls == [
        {
            "inputs": ["first", "second"],
            "kwargs": {
                "convert_to_numpy": True,
                "normalize_embeddings": True,
                "show_progress_bar": False,
            },
        }
    ]


def test_embed_text_wraps_underlying_errors() -> None:
    provider = BgeEmbeddingProvider(
        model_name="BAAI/bge-small-en-v1.5",
        model=FailingSentenceTransformer(),
    )

    with pytest.raises(InfrastructureError):
        provider.embed_text("Hydraulic pump maintenance")


def test_embed_batch_wraps_underlying_errors() -> None:
    provider = BgeEmbeddingProvider(
        model_name="BAAI/bge-small-en-v1.5",
        model=FailingSentenceTransformer(),
    )

    with pytest.raises(InfrastructureError):
        provider.embed_batch(["first", "second"])


def test_ollama_style_model_name_fails_fast() -> None:
    with pytest.raises(InfrastructureError) as exc_info:
        BgeEmbeddingProvider(model_name="Qwen/qwen3-embedding:0.6B")

    assert exc_info.value.details == {
        "model_name": "Qwen/qwen3-embedding:0.6B",
        "expected_provider": "sentence-transformers",
        "suggested_model_name": "BAAI/bge-small-en-v1.5",
    }


def test_provider_prefers_local_files_only_model_load(monkeypatch) -> None:
    LoaderSentenceTransformer.calls = []
    LoaderSentenceTransformer.fail_local_only = False
    monkeypatch.setitem(
        sys.modules,
        "sentence_transformers",
        types.SimpleNamespace(
            SentenceTransformer=LoaderSentenceTransformer,
        ),
    )
    provider = BgeEmbeddingProvider(model_name="BAAI/bge-small-en-v1.5")

    vector = provider.embed_text("Hydraulic pump maintenance")

    assert vector == [0.1, 0.2, 0.3]
    assert LoaderSentenceTransformer.calls == [
        {
            "model_name": "BAAI/bge-small-en-v1.5",
            "kwargs": {
                "local_files_only": True,
            },
        }
    ]


def test_provider_falls_back_to_default_model_load_when_local_cache_fails(
    monkeypatch,
) -> None:
    LoaderSentenceTransformer.calls = []
    LoaderSentenceTransformer.fail_local_only = True
    monkeypatch.setitem(
        sys.modules,
        "sentence_transformers",
        types.SimpleNamespace(
            SentenceTransformer=LoaderSentenceTransformer,
        ),
    )
    provider = BgeEmbeddingProvider(model_name="BAAI/bge-small-en-v1.5")

    vector = provider.embed_text("Hydraulic pump maintenance")

    assert vector == [0.1, 0.2, 0.3]
    assert LoaderSentenceTransformer.calls == [
        {
            "model_name": "BAAI/bge-small-en-v1.5",
            "kwargs": {
                "local_files_only": True,
            },
        },
        {
            "model_name": "BAAI/bge-small-en-v1.5",
            "kwargs": {},
        },
    ]
