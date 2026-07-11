from typing import Callable

from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)
from src.domain.common import ElementType
from src.domain.elements import CanonicalElement


class AssetContextResolver:
    """Resolves nearby-asset context (captions, surrounding text) for table and
    picture fragments: which neighboring elements are close enough (page-wise)
    and content-bearing enough to be folded into a table/picture chunk's text,
    truncated to a token budget.
    """

    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        asset_context_window: int,
        asset_context_max_tokens: int,
        element_contributes_to_chunk: Callable[[CanonicalElement], bool],
    ) -> None:
        self.text_splitter = text_splitter
        self.asset_context_window = asset_context_window
        self.asset_context_max_tokens = asset_context_max_tokens
        self._element_contributes_to_chunk = element_contributes_to_chunk

    def nearby_text(
        self,
        *,
        elements: list[CanonicalElement],
        index: int,
    ) -> str | None:
        if self.asset_context_window <= 0:
            return None

        current_element = elements[index]
        selected_parts: list[str] = []
        token_total = 0
        candidate_indexes = range(
            max(0, index - self.asset_context_window),
            min(len(elements), index + self.asset_context_window + 1),
        )

        for candidate_index in candidate_indexes:
            if candidate_index == index:
                continue

            candidate = elements[candidate_index]
            if not self._element_contributes_to_asset_context(candidate):
                continue

            if not self._shares_page_context(current_element, candidate):
                continue

            text = clean_chunk_text(candidate.text)
            if not text:
                continue

            remaining_tokens = self.asset_context_max_tokens - token_total
            if remaining_tokens <= 0:
                break

            text, text_token_count = self._truncate_to_token_limit(text, remaining_tokens)
            if not text:
                continue

            selected_parts.append(text)
            token_total += text_token_count

        if not selected_parts:
            return None

        return clean_chunk_text("\n\n".join(selected_parts))

    @staticmethod
    def _shares_page_context(
        current_element: CanonicalElement,
        candidate: CanonicalElement,
    ) -> bool:
        current_page = current_element.source.page_start
        candidate_page = candidate.source.page_start
        if current_page is None or candidate_page is None:
            return True
        return abs(candidate_page - current_page) <= 1

    def truncate_to_asset_context(self, text: str | None) -> tuple[str | None, int]:
        if not text:
            return None, 0
        return self._truncate_to_token_limit(text, self.asset_context_max_tokens)

    def _truncate_to_token_limit(self, text: str, max_tokens: int) -> tuple[str, int]:
        return self.text_splitter.token_counter.truncate_to_tokens_with_count(
            text, max_tokens
        )

    def _element_contributes_to_asset_context(
        self,
        element: CanonicalElement,
    ) -> bool:
        if not self._element_contributes_to_chunk(element):
            return False

        return element.element_type in {
            ElementType.TEXT,
            ElementType.LIST_ITEM,
            ElementType.KEY_VALUE,
            ElementType.CODE,
        }
