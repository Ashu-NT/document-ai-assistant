def test_contracts_can_be_imported() -> None:
    from src.application.contracts.ai import EmbeddingProvider, LLMProvider, OCRProvider
    from src.application.contracts.document import DocumentRepository
    from src.application.contracts.retrieval import VectorStore
    from src.application.contracts.unit_of_work import UnitOfWork

    assert EmbeddingProvider is not None
    assert LLMProvider is not None
    assert OCRProvider is not None
    assert DocumentRepository is not None
    assert VectorStore is not None
    assert UnitOfWork is not None