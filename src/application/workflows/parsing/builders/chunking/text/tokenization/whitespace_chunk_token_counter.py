from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter import (
    ChunkTokenCounter,
)


class WhitespaceChunkTokenCounter(ChunkTokenCounter):
    def count_tokens(self, text: str | None) -> int:
        if not text:
            return 0
        return len(text.split())

    def tail_text(self, text: str, token_count: int) -> str:
        if token_count <= 0:
            return ""
        tokens = text.split()
        if not tokens:
            return ""
        return " ".join(tokens[-token_count:])

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        if max_tokens <= 0:
            return ""
        tokens = text.split()
        if len(tokens) <= max_tokens:
            return text
        return " ".join(tokens[:max_tokens]).strip()

    def truncate_to_tokens_with_count(
        self, text: str, max_tokens: int
    ) -> tuple[str, int]:
        if max_tokens <= 0:
            return "", 0
        tokens = text.split()
        if len(tokens) <= max_tokens:
            return text, len(tokens)
        return " ".join(tokens[:max_tokens]).strip(), max_tokens

    def split_token_windows(self, text: str, max_tokens: int) -> list[str]:
        if not text:
            return []
        step = max(1, max_tokens)
        tokens = text.split()
        windows: list[str] = []
        for start in range(0, len(tokens), step):
            window = tokens[start : start + step]
            if window:
                windows.append(" ".join(window))
        return windows
