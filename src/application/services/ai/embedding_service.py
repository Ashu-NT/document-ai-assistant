from src.application.contracts.ai import EmbeddingProvider
from src.application.services.ai.chunk_embedding_enricher import enrich_embedding_text
from src.domain.document import DocumentChunk
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action


class EmbeddingService:
    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self.embedding_provider = embedding_provider

    @property
    def model_name(self) -> str:
        return getattr(self.embedding_provider, "model_name", "unknown")

    @tracked_action(
        action="ai.embedding.text_embedded",
        activity=True,
        audit=False,
        event=False,
    )
    def embed_text(
        self,
        text: str,
        activity_context: ActivityContext | None = None,
    ) -> list[float]:
        return self.embedding_provider.embed_text(text)

    @tracked_action(
        action="ai.embedding.batch_embedded",
        activity=True,
        audit=False,
        event=False,
    )
    def embed_batch(
        self,
        texts: list[str],
        activity_context: ActivityContext | None = None,
    ) -> list[list[float]]:
        return self.embedding_provider.embed_batch(texts)

    def embed_chunk(
        self,
        chunk: DocumentChunk,
        activity_context: ActivityContext | None = None,
    ) -> list[float]:
        return self.embed_text(
            self._text_from_chunk(chunk),
            activity_context=activity_context,
        )

    def embed_chunks(
        self,
        chunks: list[DocumentChunk],
        activity_context: ActivityContext | None = None,
    ) -> list[list[float]]:
        texts = [self._text_from_chunk(chunk) for chunk in chunks]
        return self.embed_batch(
            texts,
            activity_context=activity_context,
        )

    def _text_from_chunk(self, chunk: DocumentChunk) -> str:
        base = chunk.embedding_text if chunk.has_embedding_text() else chunk.content
        return enrich_embedding_text(
            base_text=base,
            chunk_type=chunk.chunk_type,
            section_path=list(chunk.section_path),
            content=chunk.content,
        )
