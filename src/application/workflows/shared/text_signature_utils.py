import re

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


def detect_scaffolding_role(content: str | None) -> str:
    """Classifies a chunk/payload's content by its scaffolding prefix
    (e.g. "Context:", "Figure:") into a role used by dedup/similarity
    policies to decide how two pieces of content relate to each other."""
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
