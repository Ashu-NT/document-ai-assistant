from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SingleColumnHeaderSpec:
    headers: tuple[str, ...]
    expects_trailing_code: bool
    expects_quantity: bool = False


class DoclingSingleColumnRowParser:
    _LEADING_CODE_PATTERN = re.compile(
        r"^(?P<code>(?:[A-Z]\.\d{2}(?:\.\d{2})+)|(?:[A-Z]\d+(?:[./-][A-Z0-9]+)*)|(?:\d+\.\d+(?:\.\d+)*))\b",
        re.IGNORECASE,
    )
    _TRAILING_CODE_PATTERN = re.compile(
        r"(?P<code>(?:-?[A-Z0-9]+(?:[./-][A-Z0-9]+)+)|(?:[A-Z]\d{3,}[A-Z0-9-]*))$",
        re.IGNORECASE,
    )
    _LEADING_QUANTITY_PATTERN = re.compile(r"^(?P<qty>\d{1,4})\s+(?P<rest>.+)$")
    _WHITESPACE_PATTERN = re.compile(r"\s+")
    _IDENTIFIER_TOKEN_PATTERN = re.compile(r"^[A-Z0-9]+(?:[./-][A-Z0-9]+)*$")
    _MATCH_NORMALIZATION_PATTERN = re.compile(r"[^a-z0-9]+")

    def enable_quantity_column_when_supported(
        self,
        rows: list[list[str]],
        *,
        header_spec: SingleColumnHeaderSpec,
    ) -> SingleColumnHeaderSpec:
        if header_spec.expects_quantity or header_spec.headers[0] not in {
            "Position No.",
            "Pos Nr.",
        }:
            return header_spec

        quantity_like_rows = 0
        structured_rows = 0
        for row in rows:
            normalized = self.normalize(row[0] if row else "")
            if not normalized:
                continue
            leading_match = self._LEADING_CODE_PATTERN.match(normalized)
            if leading_match is None:
                continue
            structured_rows += 1
            remaining = self.normalize(normalized[leading_match.end() :])
            quantity, _ = self._extract_leading_quantity(remaining)
            if quantity:
                quantity_like_rows += 1

        if structured_rows == 0 or quantity_like_rows * 2 < structured_rows:
            return header_spec

        description_headers = list(header_spec.headers[1:]) or ["Description"]
        return SingleColumnHeaderSpec(
            headers=(header_spec.headers[0], "Qty", *description_headers),
            expects_trailing_code=header_spec.expects_trailing_code,
            expects_quantity=True,
        )

    def reconstruct_row(
        self,
        value: str,
        *,
        header_spec: SingleColumnHeaderSpec,
    ) -> list[str] | None:
        normalized = self.normalize(value)
        if not normalized:
            return None

        leading_match = self._LEADING_CODE_PATTERN.match(normalized)
        if leading_match is None:
            if self._looks_like_note_row(normalized):
                return self._build_note_row(normalized, header_spec=header_spec)
            return None

        leading_code = self.normalize(leading_match.group("code"))
        remaining = self.normalize(normalized[leading_match.end() :])
        quantity = ""
        if header_spec.expects_quantity:
            quantity, remaining = self._extract_leading_quantity(remaining)
            if not quantity and self._looks_like_note_row(normalized):
                return self._build_note_row(normalized, header_spec=header_spec)
        trailing_code = ""
        if header_spec.expects_trailing_code:
            remaining, trailing_code = self._split_trailing_identifier(remaining)

        if len(header_spec.headers) == 2 and not header_spec.expects_quantity:
            if not remaining:
                return None
            return [leading_code, remaining]

        if not remaining and not trailing_code:
            return None

        values = [leading_code]
        if header_spec.expects_quantity:
            values.append(quantity)
        values.append(remaining)
        if header_spec.expects_trailing_code:
            values.append(trailing_code)
        return values

    def normalize(self, value: str | None) -> str:
        return self._WHITESPACE_PATTERN.sub(" ", str(value or "")).strip()

    def normalize_for_match(self, value: str | None) -> str:
        normalized = self.normalize(value).casefold()
        return self._MATCH_NORMALIZATION_PATTERN.sub(" ", normalized).strip()

    def _extract_leading_quantity(self, value: str) -> tuple[str, str]:
        match = self._LEADING_QUANTITY_PATTERN.match(value)
        if match is None:
            return "", value
        quantity = self.normalize(match.group("qty"))
        remainder = self.normalize(match.group("rest"))
        if not remainder:
            return "", value
        return quantity, remainder

    def _split_trailing_identifier(self, value: str) -> tuple[str, str]:
        multi_token_split = self._extract_multi_token_identifier_span(value)
        if multi_token_split is not None:
            return multi_token_split

        trailing_match = self._TRAILING_CODE_PATTERN.search(value)
        if trailing_match is not None:
            trailing_code = self.normalize(trailing_match.group("code"))
            remaining = self.normalize(value[: trailing_match.start()])
            return remaining, trailing_code

        tokens = value.split()
        for span_size in range(min(3, len(tokens)), 0, -1):
            trailing_tokens = tokens[-span_size:]
            trailing_value = self.normalize(" ".join(trailing_tokens).strip(" ,;:"))
            if not self._looks_like_identifier_span(trailing_tokens, trailing_value):
                continue
            remaining = self.normalize(" ".join(tokens[:-span_size]))
            if remaining:
                return remaining, trailing_value

        return value, ""

    def _extract_multi_token_identifier_span(self, value: str) -> tuple[str, str] | None:
        tokens = value.split()
        for span_size in range(min(3, len(tokens)), 1, -1):
            trailing_tokens = tokens[-span_size:]
            trailing_value = self.normalize(" ".join(trailing_tokens).strip(" ,;:"))
            if not self._looks_like_multi_token_identifier_span(
                trailing_tokens,
                trailing_value,
            ):
                continue
            remaining = self.normalize(" ".join(tokens[:-span_size]))
            if remaining:
                return remaining, trailing_value
        return None

    def _looks_like_identifier_span(
        self,
        tokens: list[str],
        normalized_value: str,
    ) -> bool:
        if not normalized_value or not any(character.isdigit() for character in normalized_value):
            return False

        normalized_tokens = [
            self.normalize(token.strip(" ,;:"))
            for token in tokens
            if self.normalize(token.strip(" ,;:"))
        ]
        if not normalized_tokens:
            return False

        for token in normalized_tokens:
            if token.casefold() != token and not self._IDENTIFIER_TOKEN_PATTERN.fullmatch(token):
                return False

        return any(
            any(character.isupper() for character in token)
            or any(character.isdigit() for character in token)
            for token in normalized_tokens
        )

    def _looks_like_multi_token_identifier_span(
        self,
        tokens: list[str],
        normalized_value: str,
    ) -> bool:
        if not normalized_value or not any(character.isdigit() for character in normalized_value):
            return False

        normalized_tokens = [
            self.normalize(token.strip(" ,;:"))
            for token in tokens
            if self.normalize(token.strip(" ,;:"))
        ]
        if len(normalized_tokens) < 2:
            return False

        if any(any(character.islower() for character in token) for token in normalized_tokens):
            return False

        return all(
            self._IDENTIFIER_TOKEN_PATTERN.fullmatch(token) is not None
            for token in normalized_tokens
        )

    def _looks_like_note_row(self, value: str) -> bool:
        return len(value.split()) >= 6 and self._LEADING_CODE_PATTERN.match(value) is None

    def _build_note_row(
        self,
        value: str,
        *,
        header_spec: SingleColumnHeaderSpec,
    ) -> list[str]:
        column_count = len(header_spec.headers)
        row = [""] * column_count
        description_index = column_count - 1
        if header_spec.expects_trailing_code:
            description_index -= 1
        row[description_index] = value
        return row
