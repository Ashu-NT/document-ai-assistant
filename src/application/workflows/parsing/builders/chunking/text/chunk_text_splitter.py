import re

from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter import (
    ChunkTokenCounter,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.whitespace_chunk_token_counter import (
    WhitespaceChunkTokenCounter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)


class ChunkTextSplitter:
    def __init__(
        self,
        *,
        max_chunk_tokens: int = 200,
        chunk_overlap: int = 20,
        token_counter: ChunkTokenCounter | None = None,
    ) -> None:
        self.max_chunk_tokens = max_chunk_tokens
        self.chunk_overlap = chunk_overlap
        self.token_counter = token_counter or WhitespaceChunkTokenCounter()

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

            overlapped_windows.append(
                self._prepend_overlap_within_budget(
                    previous_source_window=previous_source_window,
                    window=window,
                )
            )
            previous_source_window = source_window

        return overlapped_windows

    def _prepend_overlap_within_budget(
        self,
        *,
        previous_source_window: str,
        window: str,
    ) -> str:
        """Prepends as much of `chunk_overlap` tokens of cross-window
        context as safely fits within `max_chunk_tokens`.

        Every `window` produced by `_split_recursively` already satisfies
        `count_tokens(window) <= max_chunk_tokens` by construction - this
        method must never shrink, replace, or drop any of that payload; it
        only ever reduces how much overlap context gets prepended in front
        of it (down to zero) so the *final emitted* text still fits.

        Overlap fit is verified against the actual joined-and-retokenized
        text via `count_tokens()`, never assumed additive from independently
        counted piece lengths - a non-whitespace tokenizer's boundary
        retokenization is not guaranteed to equal a simple sum, and the
        final encoded text is what must stay within budget, not an estimate
        of it. Iterates from the full configured overlap down to the
        smallest possible (1 token), which is a small, deterministic, and
        bounded number of tokenizer calls (`chunk_overlap` is a handful of
        tokens per chunking profile), not an expensive search.
        """
        window_tokens = self.count_tokens(window)
        if window_tokens >= self.max_chunk_tokens:
            # No room for any overlap without exceeding budget by itself -
            # the payload's own content is authoritative.
            return window

        for overlap_tokens in range(self.chunk_overlap, 0, -1):
            overlap_prefix = self.token_counter.tail_text(
                previous_source_window, overlap_tokens
            )
            if not overlap_prefix:
                continue
            candidate = f"{overlap_prefix} {window}".strip()
            if self.count_tokens(candidate) <= self.max_chunk_tokens:
                return candidate

        return window

    def count_tokens(self, text: str | None) -> int:
        return self.token_counter.count_tokens(text)

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
            (self._split_clauses, " "),
        ]

        if level >= len(splitters):
            return self._split_token_windows(cleaned)

        splitter, joiner = splitters[level]
        parts = splitter(cleaned)
        if len(parts) <= 1:
            return self._split_recursively(cleaned, level + 1)

        windows: list[str] = []
        current_parts: list[str] = []
        # Tracks count_tokens(joiner.join(current_parts)) incrementally
        # instead of rejoining and retokenizing the whole accumulated text
        # on every part (which turned adding k parts into O(k^2) tokenizer
        # calls). Safe because parts are whitespace-boundary units (a full
        # paragraph/line/sentence) joined only by whitespace separators, so
        # token counts add up across the join for both the whitespace and
        # transformer counters.
        current_token_count = 0

        for part in parts:
            part = clean_chunk_text(part)
            if not part:
                continue

            part_token_count = self.count_tokens(part)
            candidate_token_count = current_token_count + part_token_count
            if candidate_token_count <= self.max_chunk_tokens:
                current_parts.append(part)
                current_token_count = candidate_token_count
                continue

            if current_parts:
                chunk_text = clean_chunk_text(joiner.join(current_parts))
                if chunk_text:
                    windows.append(chunk_text)
                current_parts = []
                current_token_count = 0

            if part_token_count <= self.max_chunk_tokens:
                current_parts = [part]
                current_token_count = part_token_count
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

    # Last semantic-boundary attempt before the raw token-window fallback
    # below, which has no awareness of sentence/clause structure at all.
    # This only matters for a single sentence long enough on its own to
    # exceed max_chunk_tokens (long compound safety-warning sentences with
    # several conditional clauses are the realistic case) -- splitting on
    # semicolons or before a comma-joined conjunction keeps each piece a
    # complete clause instead of cutting through the middle of one.
    _CLAUSE_BOUNDARY_PATTERN = re.compile(
        r"(?<=[;:])\s+|,\s+(?=(?:and|or|but|nor|unless|if|since|because|"
        r"when|while|which|that|so)\b)",
        re.IGNORECASE,
    )

    @classmethod
    def _split_clauses(cls, text: str) -> list[str]:
        return [
            part.strip()
            for part in cls._CLAUSE_BOUNDARY_PATTERN.split(text)
            if part.strip()
        ]

    def _split_token_windows(self, text: str) -> list[str]:
        return self.token_counter.split_token_windows(text, self.max_chunk_tokens)
