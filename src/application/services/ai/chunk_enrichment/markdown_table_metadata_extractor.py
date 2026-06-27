import re

from src.application.services.ai.chunk_enrichment.markdown_table_metadata import (
    MarkdownTableMetadata,
)

_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")
_UNIT_PATTERN_RE = re.compile(
    r"\b(?:bar|mbar|psi|pa|kpa|mpa|v|kv|a|ma|hz|khz|rpm|nm|n m|kw|w|kg|g|mm|cm|ml|l|hours|hour|hrs|hr|h|°c|deg c|celsius|percent)\b",
    re.IGNORECASE,
)


def extract_markdown_table_metadata(content: str) -> MarkdownTableMetadata | None:
    if not content or "|" not in content:
        return None

    lines = [line.rstrip() for line in content.splitlines()]
    table_block = _longest_table_block(lines)
    if table_block is None:
        return None

    start, end = table_block
    table_lines = lines[start:end]
    rows = [_split_markdown_row(line) for line in table_lines if _is_table_line(line)]
    if len(rows) < 2:
        return None

    headers = tuple(cell for cell in rows[0] if cell)
    body_start = 2 if len(table_lines) > 1 and _TABLE_SEPARATOR_RE.match(table_lines[1]) else 1
    body_rows = rows[body_start:]

    row_labels = _unique_preserve_order(
        row[0]
        for row in body_rows
        if row and row[0] and (not headers or row[0].lower() != headers[0].lower())
    )
    units = _extract_units(headers, body_rows)
    caption, context = _classify_intro_blocks(lines[:start])

    return MarkdownTableMetadata(
        caption=caption,
        context=context,
        headers=tuple(headers),
        row_labels=tuple(row_labels),
        units=tuple(units),
    )


def _longest_table_block(lines: list[str]) -> tuple[int, int] | None:
    best: tuple[int, int] | None = None
    start: int | None = None

    for index, line in enumerate(lines):
        is_table_line = _is_table_line(line)
        if is_table_line and start is None:
            start = index
            continue
        if not is_table_line and start is not None:
            if index - start >= 2 and (best is None or (index - start) > (best[1] - best[0])):
                best = (start, index)
            start = None

    if start is not None and len(lines) - start >= 2:
        candidate = (start, len(lines))
        if best is None or (candidate[1] - candidate[0]) > (best[1] - best[0]):
            best = candidate

    return best


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.count("|") >= 2 and stripped.startswith("|") and stripped.endswith("|")


def _split_markdown_row(line: str) -> list[str]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return [cell for cell in cells if cell]


def _classify_intro_blocks(lines: list[str]) -> tuple[str | None, str | None]:
    blocks = _text_blocks(lines)
    if not blocks:
        return (None, None)
    if len(blocks) >= 2:
        return (blocks[0], " ".join(blocks[1:]).strip() or None)

    only_block = blocks[0]
    token_count = len(only_block.split())
    lowered = only_block.lower()
    if lowered.startswith("table ") or lowered.startswith("tab.") or token_count <= 12:
        return (only_block, None)
    return (None, only_block)


def _text_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if current:
                blocks.append(" ".join(current).strip())
                current = []
            continue
        if _is_table_line(line):
            continue
        current.append(line)

    if current:
        blocks.append(" ".join(current).strip())

    return [block for block in blocks if block]


def _extract_units(headers: tuple[str, ...], body_rows: list[list[str]]) -> list[str]:
    values: list[str] = []
    for header in headers:
        values.extend(_UNIT_PATTERN_RE.findall(header))
    for row in body_rows:
        if not row:
            continue
        for cell in row[1:]:
            values.extend(_UNIT_PATTERN_RE.findall(cell))
    return _unique_preserve_order(value.lower() for value in values if value)


def _unique_preserve_order(values) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        cleaned = str(value).strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        ordered.append(cleaned)
    return ordered
