from dataclasses import dataclass

from src.application.workflows.shared.text_signature_utils import (
    detect_scaffolding_role as detect_chunk_role,
    extract_identifier_tokens,
    normalize_free_text,
    strip_scaffolding_prefixes,
    tokenize_text,
)
from src.domain.retrieval import RetrievedChunk


@dataclass(slots=True, frozen=True)
class RetrievedChunkSignature:
    role: str
    normalized_content: str
    normalized_stripped_content: str
    token_set: frozenset[str]
    stripped_token_set: frozenset[str]
    identifier_tokens: frozenset[str]
    is_table_like: bool
    sequence_number: int

    @classmethod
    def from_chunk(
        cls,
        chunk: RetrievedChunk,
    ) -> "RetrievedChunkSignature":
        stripped_content = strip_scaffolding_prefixes(chunk.content)
        return cls(
            role=detect_chunk_role(chunk.content),
            normalized_content=normalize_free_text(chunk.content),
            normalized_stripped_content=normalize_free_text(stripped_content),
            token_set=frozenset(tokenize_text(chunk.content)),
            stripped_token_set=frozenset(tokenize_text(stripped_content)),
            identifier_tokens=frozenset(extract_identifier_tokens(chunk.content)),
            is_table_like=chunk.chunk_type.value == "spare_parts_table"
            or "|" in chunk.content,
            sequence_number=_coerce_int(chunk.metadata.get("sequence_number")) or 10**6,
        )


def _coerce_int(value: object) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None
