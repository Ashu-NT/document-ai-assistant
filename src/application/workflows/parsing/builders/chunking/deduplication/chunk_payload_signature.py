import re
from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_IDENTIFIER_PATTERN = re.compile(
    r"(?i)\b(?:[a-z]+[a-z0-9./-]*\d[a-z0-9./-]*|\d+(?:[./-]\d+)+)\b"
)
_STRUCTURED_ITEM_LABEL_PATTERN = re.compile(
    r"(?im)^\s*(\d{1,4})\s*-\s*[a-z]"
)
_OVERVIEW_PREFIXES = ("section overview:",)
_CONTEXT_PREFIXES = ("context:",)
_ASSET_PREFIXES = ("figure:", "ocr:")
_ORDERED_PREFIXES = (
    *_OVERVIEW_PREFIXES,
    *_CONTEXT_PREFIXES,
    *_ASSET_PREFIXES,
)


@dataclass(slots=True, frozen=True)
class ChunkPayloadSignature:
    role: str
    normalized_content: str
    normalized_stripped_content: str
    token_set: frozenset[str]
    stripped_token_set: frozenset[str]
    identifier_tokens: frozenset[str]
    is_table_like: bool
    has_subsection_summary: bool

    @classmethod
    def from_payload(
        cls,
        payload: ChunkPayload,
    ) -> "ChunkPayloadSignature":
        stripped_content = strip_scaffolding_prefixes(payload.content)
        return cls(
            role=detect_payload_role(payload.content),
            normalized_content=normalize_free_text(payload.content),
            normalized_stripped_content=normalize_free_text(stripped_content),
            token_set=frozenset(tokenize_text(payload.content)),
            stripped_token_set=frozenset(tokenize_text(stripped_content)),
            identifier_tokens=frozenset(extract_identifier_tokens(payload.content)),
            is_table_like=payload.chunk_type.value == "spare_parts_table"
            or bool(payload.table_ids)
            or "|" in payload.content,
            has_subsection_summary="subsections:" in (payload.content or "").lower(),
        )


def detect_payload_role(content: str | None) -> str:
    first_line = _first_non_empty_line(content).lower()
    if first_line.startswith(_OVERVIEW_PREFIXES):
        return "overview_companion"
    if first_line.startswith(_CONTEXT_PREFIXES):
        return "context_companion"
    if first_line.startswith(_ASSET_PREFIXES):
        return "asset_companion"
    return "atomic_evidence"


def strip_scaffolding_prefixes(content: str | None) -> str:
    if not content:
        return ""

    cleaned_lines: list[str] = []
    for raw_line in str(content).splitlines():
        line = raw_line.strip()
        if not line:
            continue

        lowered = line.lower()
        for prefix in _ORDERED_PREFIXES:
            if lowered.startswith(prefix):
                line = line[len(prefix):].strip(" :-")
                lowered = line.lower()
                break

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def normalize_free_text(value: str | None) -> str:
    if not value:
        return ""

    tokens = _TOKEN_PATTERN.findall(value.lower())
    return " ".join(tokens)


def tokenize_text(value: str | None) -> list[str]:
    normalized = normalize_free_text(value)
    if not normalized:
        return []
    return normalized.split()


def extract_identifier_tokens(value: str | None) -> list[str]:
    if not value:
        return []
    return sorted(
        _identifier_token_set(value)
    )


def _identifier_token_set(value: str) -> set[str]:
    tokens = {
        token.lower()
        for token in _IDENTIFIER_PATTERN.findall(value)
    }
    tokens.update(_extract_structured_item_labels(value))
    return tokens


def _extract_structured_item_labels(value: str) -> set[str]:
    return {
        f"item_label:{match.group(1)}"
        for match in _STRUCTURED_ITEM_LABEL_PATTERN.finditer(value)
    }


def _first_non_empty_line(content: str | None) -> str:
    if not content:
        return ""

    for line in str(content).splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned
    return ""
