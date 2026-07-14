from __future__ import annotations

import re

from src.application.workflows.parsing.tables.table_header_signature_builder import (
    TableHeaderSignatureBuilder,
)
from src.domain.assets import TableAsset

_SEPARATOR_PATTERN = re.compile(r"[^\w]+")


class TableHeaderCompatibilityMatcher:
    def __init__(
        self,
        *,
        header_signature_builder: TableHeaderSignatureBuilder | None = None,
    ) -> None:
        self.header_signature_builder = (
            header_signature_builder or TableHeaderSignatureBuilder()
        )

    def are_compatible(
        self,
        previous_table: TableAsset,
        current_table: TableAsset,
    ) -> bool:
        previous_signature = self.header_signature_builder.build(previous_table)
        current_signature = self.header_signature_builder.build(current_table)
        if previous_signature and previous_signature == current_signature:
            return True

        previous_header_text = self._collapsed_header_text(previous_table)
        current_header_text = self._collapsed_header_text(current_table)
        if not previous_header_text or not current_header_text:
            return False
        if previous_header_text == current_header_text:
            return True

        previous_tokens = tuple(previous_header_text.split())
        current_tokens = tuple(current_header_text.split())
        if not previous_tokens or not current_tokens:
            return False

        overlap = len(set(previous_tokens) & set(current_tokens))
        longest = max(len(set(previous_tokens)), len(set(current_tokens)))
        if longest <= 0:
            return False

        return overlap / longest >= 0.8

    @staticmethod
    def _collapsed_header_text(table: TableAsset) -> str | None:
        header_paths = TableHeaderSignatureBuilder().build_paths(table)
        if not header_paths:
            return None
        header_parts = []
        for path in header_paths:
            normalized_path = [
                _normalize_token_text(part) for part in path if _normalize_token_text(part)
            ]
            if normalized_path:
                header_parts.extend(normalized_path)
        if not header_parts:
            return None
        return " ".join(header_parts)


def _normalize_token_text(value: str | None) -> str:
    text = _SEPARATOR_PATTERN.sub(" ", str(value or "").casefold()).strip()
    return " ".join(text.split())
