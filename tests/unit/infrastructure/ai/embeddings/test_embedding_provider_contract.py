import pytest
from unittest.mock import MagicMock, patch

from src.application.contracts.ai.embedding_provider import EmbeddingProvider
from src.application.services.ai.embedding_service import EmbeddingService
from src.infrastructure.ai.embeddings.bge_embedding_provider import BgeEmbeddingProvider
from src.infrastructure.ai.embeddings.ollama_embedding_provider import OllamaEmbeddingProvider


class TestEmbeddingProviderProtocol:
    def test_bge_provider_satisfies_protocol(self):
        mock_model = MagicMock()
        mock_model.encode.return_value = [0.1, 0.2, 0.3]
        provider = BgeEmbeddingProvider(model_name="BAAI/bge-small-en-v1.5", model=mock_model)
        assert isinstance(provider, EmbeddingProvider)
        assert hasattr(provider, "model_name")
        assert hasattr(provider, "embed_text")
        assert hasattr(provider, "embed_batch")

    def test_bge_provider_model_name_preserved(self):
        mock_model = MagicMock()
        provider = BgeEmbeddingProvider(model_name="BAAI/bge-small-en-v1.5", model=mock_model)
        assert provider.model_name == "BAAI/bge-small-en-v1.5"

    def test_ollama_provider_satisfies_protocol(self):
        provider = OllamaEmbeddingProvider(model_name="nomic-embed-text")
        assert isinstance(provider, EmbeddingProvider)
        assert hasattr(provider, "model_name")
        assert provider.model_name == "nomic-embed-text"

    def test_ollama_provider_embed_text_raises_on_missing_ollama(self):
        provider = OllamaEmbeddingProvider()
        with patch.dict("sys.modules", {"ollama": None}):
            from src.shared.exceptions import InfrastructureError
            with pytest.raises((InfrastructureError, ImportError, Exception)):
                provider.embed_text("test text")


class TestEmbeddingServiceModelName:
    def test_service_exposes_provider_model_name(self):
        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.model_name = "test-model-v1"
        service = EmbeddingService(mock_provider)
        assert service.model_name == "test-model-v1"

    def test_service_returns_unknown_when_provider_has_no_model_name(self):
        mock_provider = MagicMock()
        del mock_provider.model_name
        service = EmbeddingService(mock_provider)
        assert service.model_name == "unknown"
