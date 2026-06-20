from pathlib import Path
from typing import Any

from src.application.contracts.ai import EmbeddingProvider
from src.shared.exceptions import InfrastructureError

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


def _default_embedding_model_name() -> str:
    try:
        from src.config.settings import embedding_settings

        return embedding_settings.model_name or DEFAULT_EMBEDDING_MODEL
    except Exception:
        return DEFAULT_EMBEDDING_MODEL


class BgeEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        *,
        model_name: str | None = None,
        normalize_embeddings: bool = True,
        model: Any | None = None,
    ) -> None:
        self.model_name = model_name or _default_embedding_model_name()
        self.normalize_embeddings = normalize_embeddings
        self._model = model
        if self._model is None:
            self._validate_model_name(self.model_name)

    def embed_text(self, text: str) -> list[float]:
        try:
            embedding = self._get_model().encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise InfrastructureError(
                "Failed to generate text embedding.",
                details={"model_name": self.model_name},
            ) from exc

        return self._normalize_vector(embedding)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            embeddings = self._get_model().encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise InfrastructureError(
                "Failed to generate batch embeddings.",
                details={
                    "model_name": self.model_name,
                    "batch_size": len(texts),
                },
            ) from exc

        return self._normalize_matrix(embeddings)

    def _get_model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)

        return self._model

    @staticmethod
    def _normalize_vector(vector: Any) -> list[float]:
        if hasattr(vector, "tolist"):
            vector = vector.tolist()

        if isinstance(vector, tuple):
            vector = list(vector)

        if not isinstance(vector, list):
            vector = list(vector)

        return [float(value) for value in vector]

    @classmethod
    def _normalize_matrix(cls, embeddings: Any) -> list[list[float]]:
        if hasattr(embeddings, "tolist"):
            embeddings = embeddings.tolist()

        if isinstance(embeddings, tuple):
            embeddings = list(embeddings)

        if not isinstance(embeddings, list):
            embeddings = list(embeddings)

        if embeddings and isinstance(embeddings[0], (int, float)):
            return [cls._normalize_vector(embeddings)]

        return [cls._normalize_vector(embedding) for embedding in embeddings]

    @classmethod
    def _validate_model_name(cls, model_name: str) -> None:
        if cls._looks_like_ollama_model_name(model_name):
            raise InfrastructureError(
                "BgeEmbeddingProvider requires a sentence-transformers or Hugging Face model id, not an Ollama-style model tag.",
                details={
                    "model_name": model_name,
                    "expected_provider": "sentence-transformers",
                    "suggested_model_name": DEFAULT_EMBEDDING_MODEL,
                },
            )

    @staticmethod
    def _looks_like_ollama_model_name(model_name: str) -> bool:
        if not model_name:
            return False

        if "\\" in model_name or Path(model_name).anchor:
            return False

        last_segment = model_name.rsplit("/", maxsplit=1)[-1]
        return ":" in last_segment
