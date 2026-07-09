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
    def truncate_to_tokens_with_count(
        self, text: str, max_tokens: int
    ) -> tuple[str, int]:
        """Like truncate_to_tokens(), but also returns the truncated text's
        own token count -- callers that need both avoid re-tokenizing the
        (already truncated) text a second time just to count it."""
        raise NotImplementedError

    @abstractmethod
    def split_token_windows(self, text: str, max_tokens: int) -> list[str]:
        raise NotImplementedError
