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
