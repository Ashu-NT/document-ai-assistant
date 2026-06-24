from __future__ import annotations

from src.application.contracts.ai import EmbeddingProvider


def create_embedding_provider() -> EmbeddingProvider:
    """Instantiate the embedding provider selected via EMBEDDING_PROVIDER env var.

    Reads from ``embedding_settings.embedding_provider``:
    - ``"bge"``    — BgeEmbeddingProvider (sentence-transformers, default)
    - ``"ollama"`` — OllamaEmbeddingProvider (requires Ollama running locally)

    Falls back to BGE when the value is unrecognised.
    """
    from src.config.settings import embedding_settings, llm_settings
    from src.infrastructure.ai.embeddings.bge_embedding_provider import (
        BgeEmbeddingProvider,
    )
    from src.infrastructure.ai.embeddings.ollama_embedding_provider import (
        OllamaEmbeddingProvider,
    )

    provider_name = (embedding_settings.embedding_provider or "bge").strip().lower()

    if provider_name == "ollama":
        return OllamaEmbeddingProvider(
            model_name=embedding_settings.ollama_embedding_model,
            base_url=llm_settings.ollama_base_url,
        )

    return BgeEmbeddingProvider(model_name=embedding_settings.model_name)
