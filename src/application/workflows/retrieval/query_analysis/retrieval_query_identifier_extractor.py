import re
from dataclasses import dataclass

from src.application.workflows.retrieval.deduplication.retrieved_chunk_signature import (
    extract_identifier_tokens,
)

# Same value shape as the generic catch-all in text_signature_utils.py's
# _IDENTIFIER_PATTERN (alphanumeric-with-a-digit, or digit groups joined by
# separators) -- kept in sync deliberately so a value recognized by a typed
# pattern below is always also one the generic pattern would have matched.
_VALUE_PATTERN = r"[a-z]+[a-z0-9./-]*\d[a-z0-9./-]*|\d+(?:[./-]\d+)+"

_PART_NUMBER_LABEL = r"(?:part\s*(?:no\.?|nr\.?|number)?|p\s*/\s*n)"
_SERIAL_NUMBER_LABEL = r"(?:serial\s*(?:no\.?|nr\.?|number)?|s\s*/\s*no?)"
_MODEL_NUMBER_LABEL = r"model\s*(?:no\.?|nr\.?|number)?"
_DRAWING_NUMBER_LABEL = r"(?:drawing|dwg\.?)\s*(?:no\.?|nr\.?|number)?"
_CERTIFICATE_NUMBER_LABEL = r"cert(?:ificate)?\.?\s*(?:no\.?|nr\.?|number)?"
_ORDER_CODE_LABEL = r"order(?:ing)?\s*(?:code|no\.?|nr\.?|number)?"
_TAG_NUMBER_LABEL = r"tag\s*(?:no\.?|nr\.?|number)?"

# Label patterns tolerate both the abbreviated ("part no.", "p/n") and
# expanded ("part number") forms, since this extractor runs on the query's
# ORIGINAL text -- RetrievalQueryAnalyzer.analyze() extracts identifiers
# before handing off to RetrievalQueryRewriter, so a value can appear next
# to either form.
_TYPED_IDENTIFIER_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (identifier_type, re.compile(rf"(?i)\b{label}\s*[:#]?\s*({_VALUE_PATTERN})\b"))
    for identifier_type, label in (
        ("part_number", _PART_NUMBER_LABEL),
        ("serial_number", _SERIAL_NUMBER_LABEL),
        ("model_number", _MODEL_NUMBER_LABEL),
        ("drawing_number", _DRAWING_NUMBER_LABEL),
        ("certificate_number", _CERTIFICATE_NUMBER_LABEL),
        ("order_code", _ORDER_CODE_LABEL),
        ("tag_number", _TAG_NUMBER_LABEL),
    )
)


@dataclass(frozen=True, slots=True)
class TypedIdentifierMatch:
    value: str
    identifier_type: str


class RetrievalQueryIdentifierExtractor:
    def extract(
        self,
        query_text: str | None,
    ) -> list[str]:
        return extract_identifier_tokens(query_text)

    def extract_typed(self, query_text: str | None) -> list[TypedIdentifierMatch]:
        """Additive to extract(): recognizes common identifier FORMATS
        (part/serial/model/drawing/certificate number, order code, tag
        number) from their contextual label, in addition to extract()'s
        generic catch-all pattern. Values not claimed by a typed pattern
        are still included, tagged "unknown" -- the generic pattern remains
        the safety net for anything the format-specific patterns miss.

        Consumed by RetrievalQueryChunkTypePreferenceMapper to promote the
        chunk type matching a specifically-typed identifier format (e.g. a
        drawing number promotes DRAWING_REFERENCE) ahead of the IDENTIFIER
        intent's generic preference order. Kept separate from extract()'s
        list[str] contract, which RetrievalQuery.detected_identifiers relies
        on and callers like IdentifierEvidenceGuardrail don't need typing for.
        """
        if not query_text:
            return []

        matches: list[TypedIdentifierMatch] = []
        seen_values: set[str] = set()
        for identifier_type, pattern in _TYPED_IDENTIFIER_PATTERNS:
            for match in pattern.finditer(query_text):
                value = match.group(1).lower()
                if value in seen_values:
                    continue
                seen_values.add(value)
                matches.append(
                    TypedIdentifierMatch(value=value, identifier_type=identifier_type)
                )

        for value in extract_identifier_tokens(query_text):
            if value in seen_values:
                continue
            seen_values.add(value)
            matches.append(TypedIdentifierMatch(value=value, identifier_type="unknown"))

        return matches
