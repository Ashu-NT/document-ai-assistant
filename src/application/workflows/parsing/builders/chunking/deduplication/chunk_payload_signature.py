from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.application.workflows.shared.text_signature_utils import (
    detect_scaffolding_role as detect_payload_role,
    extract_identifier_tokens,
    normalize_free_text,
    strip_scaffolding_prefixes,
    tokenize_text,
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
