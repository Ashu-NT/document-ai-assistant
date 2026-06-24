from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class EmbeddingSettings(AppBaseSettings):
    model_name: str = Field(alias="EMBEDDING_MODEL")
    dimensions: int = Field(alias="EMBEDDING_DIMENSIONS")

    # Which embedding backend to use: "bge" (default) or "ollama".
    # Set EMBEDDING_PROVIDER=ollama in .env to switch to an Ollama-served model.
    embedding_provider: str = Field(default="bge", alias="EMBEDDING_PROVIDER")

    # Ollama embedding model name — only used when EMBEDDING_PROVIDER=ollama.
    ollama_embedding_model: str = Field(
        default="nomic-embed-text", alias="OLLAMA_EMBEDDING_MODEL"
    )

        