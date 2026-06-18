from src.application.services.retrieval.hybrid_retrieval_service import (
    HybridRetrievalService,
)


class RetrievalApplicationService:
    def __init__(self, hybrid: HybridRetrievalService) -> None:
        self.hybrid = hybrid