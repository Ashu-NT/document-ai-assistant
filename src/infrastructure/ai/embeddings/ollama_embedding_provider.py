from __future__ import annotations

from src.application.contracts.ai import EmbeddingProvider
from src.shared.exceptions import InfrastructureError

DEFAULT_OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by an Ollama embeddings endpoint.

    This is a stub implementation for local development and testing.
    Switch to this provider to use any Ollama-served embedding model
    (e.g. nomic-embed-text, mxbai-embed-large) without changing downstream code.
    """

    def __init__(
        self,
        *,
        model_name: str = DEFAULT_OLLAMA_EMBEDDING_MODEL,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url

    def embed_text(self, text: str) -> list[float]:
        try:
            import ollama  # type: ignore[import-untyped]
        except ImportError as exc:
            raise InfrastructureError(
                "ollama package is required for OllamaEmbeddingProvider.",
                details={"model_name": self.model_name},
            ) from exc
        try:
            response = ollama.embeddings(model=self.model_name, prompt=text)
            return list(response["embedding"])
        except Exception as exc:
            raise InfrastructureError(
                "Failed to generate text embedding via Ollama.",
                details={"model_name": self.model_name, "base_url": self.base_url},
            ) from exc

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]
