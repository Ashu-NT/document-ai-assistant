from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    extract_identifier_tokens,
)


class RetrievalQueryIdentifierExtractor:
    def extract(
        self,
        query_text: str | None,
    ) -> list[str]:
        return extract_identifier_tokens(query_text)
