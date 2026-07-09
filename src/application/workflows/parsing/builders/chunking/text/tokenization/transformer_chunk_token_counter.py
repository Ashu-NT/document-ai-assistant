from typing import Any

from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter import (
    ChunkTokenCounter,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.whitespace_chunk_token_counter import (
    WhitespaceChunkTokenCounter,
)
from src.shared.exceptions import InfrastructureError


class TransformerChunkTokenCounter(ChunkTokenCounter):
    def __init__(
        self,
        *,
        tokenizer: Any,
        model_name: str | None = None,
    ) -> None:
        self.tokenizer = tokenizer
        self.model_name = model_name or getattr(tokenizer, "name_or_path", "unknown")
        self._fallback = WhitespaceChunkTokenCounter()

    @classmethod
    def from_pretrained(
        cls,
        *,
        model_name: str,
        local_files_only: bool = True,
    ) -> "TransformerChunkTokenCounter":
        try:
            from transformers import AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                pretrained_model_name_or_path=model_name,
                local_files_only=local_files_only,
            )
        except Exception as exc:
            raise InfrastructureError(
                "Failed to load transformer tokenizer for chunking.",
                details={
                    "model_name": model_name,
                    "local_files_only": local_files_only,
                },
            ) from exc

        return cls(tokenizer=tokenizer, model_name=model_name)

    def count_tokens(self, text: str | None) -> int:
        if not text:
            return 0

        offsets = self._token_offsets(text)
        if offsets:
            return len(offsets)

        try:
            if hasattr(self.tokenizer, "tokenize"):
                return len(self.tokenizer.tokenize(text))
            encoded = self.tokenizer(
                text,
                add_special_tokens=False,
                truncation=False,
            )
            input_ids = encoded.get("input_ids", [])
            return len(input_ids)
        except Exception:
            return self._fallback.count_tokens(text)

    def tail_text(self, text: str, token_count: int) -> str:
        if token_count <= 0:
            return ""

        offsets = self._token_offsets(text)
        if not offsets:
            return self._fallback.tail_text(text, token_count)

        start_index = max(0, len(offsets) - token_count)
        start_char = offsets[start_index][0]
        return text[start_char:].strip()

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        if max_tokens <= 0:
            return ""

        offsets = self._token_offsets(text)
        if not offsets:
            return self._fallback.truncate_to_tokens(text, max_tokens)

        if len(offsets) <= max_tokens:
            return text

        end_char = offsets[max_tokens - 1][1]
        return text[:end_char].strip()

    def truncate_to_tokens_with_count(
        self, text: str, max_tokens: int
    ) -> tuple[str, int]:
        if max_tokens <= 0:
            return "", 0

        offsets = self._token_offsets(text)
        if not offsets:
            return self._fallback.truncate_to_tokens_with_count(text, max_tokens)

        if len(offsets) <= max_tokens:
            return text, len(offsets)

        end_char = offsets[max_tokens - 1][1]
        return text[:end_char].strip(), max_tokens

    def split_token_windows(self, text: str, max_tokens: int) -> list[str]:
        if not text:
            return []

        window_size = max(1, max_tokens)
        offsets = self._token_offsets(text)
        if not offsets:
            return self._fallback.split_token_windows(text, window_size)

        if len(offsets) <= window_size:
            return [text]

        windows: list[str] = []
        for start_index in range(0, len(offsets), window_size):
            end_index = min(start_index + window_size, len(offsets)) - 1
            start_char = offsets[start_index][0]
            end_char = offsets[end_index][1]
            segment = text[start_char:end_char].strip()
            if segment:
                windows.append(segment)
        return windows

    def _token_offsets(self, text: str) -> list[tuple[int, int]]:
        try:
            encoded = self.tokenizer(
                text,
                add_special_tokens=False,
                return_offsets_mapping=True,
                truncation=False,
            )
        except Exception:
            return []

        raw_offsets = encoded.get("offset_mapping")
        if raw_offsets is None:
            return []

        offsets: list[tuple[int, int]] = []
        for raw_offset in raw_offsets:
            if not isinstance(raw_offset, (tuple, list)) or len(raw_offset) != 2:
                continue

            start_char = int(raw_offset[0])
            end_char = int(raw_offset[1])
            if end_char <= start_char:
                continue

            offsets.append((start_char, end_char))

        return offsets
