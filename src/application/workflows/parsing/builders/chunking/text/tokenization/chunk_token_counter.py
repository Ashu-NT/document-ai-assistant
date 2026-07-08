from abc import ABC, abstractmethod


class ChunkTokenCounter(ABC):
    @abstractmethod
    def count_tokens(self, text: str | None) -> int:
        raise NotImplementedError

    @abstractmethod
    def tail_text(self, text: str, token_count: int) -> str:
        raise NotImplementedError

    @abstractmethod
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        raise NotImplementedError

    @abstractmethod
    def split_token_windows(self, text: str, max_tokens: int) -> list[str]:
        raise NotImplementedError
