from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter import (
    ChunkTokenCounter,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.transformer_chunk_token_counter import (
    TransformerChunkTokenCounter,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.whitespace_chunk_token_counter import (
    WhitespaceChunkTokenCounter,
)
from src.config.logging import get_logger
from src.shared.exceptions import InfrastructureError

logger = get_logger(__name__)

_DEFAULT_TRANSFORMER_CHUNK_TOKENIZER_MODEL = "BAAI/bge-small-en-v1.5"


def _default_provider() -> str:
    try:
        from src.config.settings import chunking_settings

        return chunking_settings.token_counter_provider
    except Exception:
        return "whitespace"


def _default_tokenizer_model() -> str:
    try:
        from src.config.settings import chunking_settings, embedding_settings

        return (
            chunking_settings.tokenizer_model
            or embedding_settings.model_name
            or _DEFAULT_TRANSFORMER_CHUNK_TOKENIZER_MODEL
        )
    except Exception:
        return _DEFAULT_TRANSFORMER_CHUNK_TOKENIZER_MODEL


def _default_tokenizer_local_only() -> bool:
    try:
        from src.config.settings import chunking_settings

        return chunking_settings.tokenizer_local_only
    except Exception:
        return True


class ChunkTokenCounterFactory:
    def __init__(
        self,
        *,
        provider: str | None = None,
        tokenizer_model: str | None = None,
        tokenizer_local_only: bool | None = None,
    ) -> None:
        self.provider = provider
        self.tokenizer_model = tokenizer_model
        self.tokenizer_local_only = tokenizer_local_only
        self._cache: dict[tuple[str, str, bool], ChunkTokenCounter] = {}

    def create(self) -> ChunkTokenCounter:
        provider = (self.provider or _default_provider()).strip().lower()
        if provider in {"", "whitespace"}:
            cache_key = ("whitespace", "", True)
            cached = self._cache.get(cache_key)
            if cached is None:
                cached = WhitespaceChunkTokenCounter()
                self._cache[cache_key] = cached
            return cached

        if provider == "transformer":
            model_name = self.tokenizer_model or _default_tokenizer_model()
            local_only = (
                self.tokenizer_local_only
                if self.tokenizer_local_only is not None
                else _default_tokenizer_local_only()
            )
            cache_key = (provider, model_name, local_only)
            cached = self._cache.get(cache_key)
            if cached is None:
                try:
                    cached = TransformerChunkTokenCounter.from_pretrained(
                        model_name=model_name,
                        local_files_only=local_only,
                    )
                except InfrastructureError:
                    logger.warning(
                        "transformer tokenizer unavailable, falling back to whitespace "
                        "token counting (chunk sizes will be measured in words, not "
                        "real subword tokens)",
                        extra={"model_name": model_name, "local_files_only": local_only},
                    )
                    cache_key = ("whitespace", "", True)
                    cached = self._cache.get(cache_key)
                    if cached is None:
                        cached = WhitespaceChunkTokenCounter()
                self._cache[cache_key] = cached
            return cached

        raise InfrastructureError(
            "Unsupported chunk token counter provider configured.",
            details={
                "provider": provider,
                "supported_providers": ["whitespace", "transformer"],
            },
        )
