import re

from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    count_tokens,
    tail_words,
)


class ChunkTextSplitter:
    def __init__(
        self,
        *,
        max_chunk_tokens: int = 200,
        chunk_overlap: int = 20,
    ) -> None:
        self.max_chunk_tokens = max_chunk_tokens
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        cleaned = clean_chunk_text(text)
        if not cleaned:
            return []

        if self.count_tokens(cleaned) <= self.max_chunk_tokens:
            return [cleaned]

        windows = self._split_recursively(cleaned)
        if len(windows) <= 1 or self.chunk_overlap <= 0:
            return windows

        overlapped_windows: list[str] = []
        previous_source_window: str | None = None

        for window in windows:
            source_window = window
            if previous_source_window is None:
                overlapped_windows.append(window)
                previous_source_window = source_window
                continue

            overlap_prefix = tail_words(
                previous_source_window,
                self.chunk_overlap,
            )
            if overlap_prefix:
                window = f"{overlap_prefix} {window}".strip()

            overlapped_windows.append(window)
            previous_source_window = source_window

        return overlapped_windows

    def count_tokens(self, text: str | None) -> int:
        return count_tokens(text)

    def _split_recursively(
        self,
        text: str,
        level: int = 0,
    ) -> list[str]:
        cleaned = clean_chunk_text(text)
        if not cleaned:
            return []

        if self.count_tokens(cleaned) <= self.max_chunk_tokens:
            return [cleaned]

        splitters = [
            (self._split_paragraphs, "\n\n"),
            (self._split_lines, "\n"),
            (self._split_sentences, " "),
        ]

        if level >= len(splitters):
            return self._split_words(cleaned)

        splitter, joiner = splitters[level]
        parts = splitter(cleaned)
        if len(parts) <= 1:
            return self._split_recursively(cleaned, level + 1)

        windows: list[str] = []
        current_parts: list[str] = []

        for part in parts:
            part = clean_chunk_text(part)
            if not part:
                continue

            candidate_parts = [*current_parts, part]
            candidate_text = joiner.join(candidate_parts)
            if self.count_tokens(candidate_text) <= self.max_chunk_tokens:
                current_parts = candidate_parts
                continue

            if current_parts:
                chunk_text = clean_chunk_text(joiner.join(current_parts))
                if chunk_text:
                    windows.append(chunk_text)
                current_parts = []

            if self.count_tokens(part) <= self.max_chunk_tokens:
                current_parts = [part]
                continue

            windows.extend(self._split_recursively(part, level + 1))

        if current_parts:
            chunk_text = clean_chunk_text(joiner.join(current_parts))
            if chunk_text:
                windows.append(chunk_text)

        return windows

    @staticmethod
    def _split_paragraphs(text: str) -> list[str]:
        return [part.strip() for part in re.split(r"\n\s*\n+", text) if part.strip()]

    @staticmethod
    def _split_lines(text: str) -> list[str]:
        return [part.strip() for part in text.splitlines() if part.strip()]

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        return [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", text)
            if part.strip()
        ]

    def _split_words(self, text: str) -> list[str]:
        tokens = text.split()
        if not tokens:
            return []

        windows: list[str] = []
        step = max(1, self.max_chunk_tokens)

        for start in range(0, len(tokens), step):
            window = tokens[start : start + self.max_chunk_tokens]
            if window:
                windows.append(" ".join(window))

        return windows
