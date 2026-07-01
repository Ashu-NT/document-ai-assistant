from src.application.workflows.extraction.extraction_batch import ExtractionBatch
from src.domain.document import DocumentChunk


class ExtractionChunkBatcher:
    def __init__(
        self,
        *,
        max_chunks_per_batch: int,
        max_chars_per_batch: int,
    ) -> None:
        self.max_chunks_per_batch = max(1, max_chunks_per_batch)
        self.max_chars_per_batch = max(1_000, max_chars_per_batch)

    def build_batches(self, chunks: list[DocumentChunk]) -> list[ExtractionBatch]:
        if not chunks:
            return []

        raw_batches: list[list[DocumentChunk]] = []
        current_batch: list[DocumentChunk] = []
        current_chars = 0

        for chunk in chunks:
            estimated_chars = self._estimate_chunk_chars(chunk)
            would_exceed_chunk_count = len(current_batch) >= self.max_chunks_per_batch
            would_exceed_char_limit = (
                current_batch
                and current_chars + estimated_chars > self.max_chars_per_batch
            )
            if would_exceed_chunk_count or would_exceed_char_limit:
                raw_batches.append(current_batch)
                current_batch = []
                current_chars = 0

            current_batch.append(chunk)
            current_chars += estimated_chars

        if current_batch:
            raw_batches.append(current_batch)

        batch_count = len(raw_batches)
        return [
            ExtractionBatch(
                batch_index=index,
                batch_count=batch_count,
                chunks=list(batch_chunks),
                char_count=sum(self._estimate_chunk_chars(chunk) for chunk in batch_chunks),
                word_count=sum(self._estimate_chunk_words(chunk) for chunk in batch_chunks),
            )
            for index, batch_chunks in enumerate(raw_batches, start=1)
        ]

    @staticmethod
    def _estimate_chunk_chars(chunk: DocumentChunk) -> int:
        section_path_text = " > ".join(chunk.section_path)
        return len(chunk.content) + len(section_path_text) + 160

    @staticmethod
    def _estimate_chunk_words(chunk: DocumentChunk) -> int:
        statistics = chunk.statistics
        if statistics is not None and statistics.token_count_estimate is not None:
            return statistics.token_count_estimate
        return max(1, len(chunk.content.split()))
