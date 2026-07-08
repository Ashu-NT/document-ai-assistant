from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter import (
    ChunkTokenCounter,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter_factory import (
    ChunkTokenCounterFactory,
)
from src.domain.document.value_objects import ChunkStatistics


class ChunkStatisticsBuilder:
    def __init__(
        self,
        *,
        token_counter: ChunkTokenCounter | None = None,
        token_counter_factory: ChunkTokenCounterFactory | None = None,
    ) -> None:
        self._token_counter = token_counter
        self._token_counter_factory = token_counter_factory or ChunkTokenCounterFactory()

    @property
    def token_counter(self) -> ChunkTokenCounter:
        if self._token_counter is None:
            self._token_counter = self._token_counter_factory.create()
        return self._token_counter

    def build(self, text: str) -> ChunkStatistics:
        safe_text = text or ""
        token_count = self.token_counter.count_tokens(safe_text)
        return ChunkStatistics(
            char_count=len(safe_text),
            token_count_estimate=max(1, token_count),
        )
