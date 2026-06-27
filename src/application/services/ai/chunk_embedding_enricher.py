from src.application.services.ai.chunk_enrichment import (
    ENRICHED_CHUNK_TYPES,
    build_chunk_related_terms,
    build_maintenance_spec_terms,
    chunk_type_label,
    extract_markdown_table_metadata,
)
from src.domain.common import ChunkType


def maintenance_spec_aliases(*, content: str, section_path: list[str]) -> str | None:
    aliases = build_maintenance_spec_terms(content=content, section_path=section_path)
    return ", ".join(aliases) if aliases else None


def enrich_embedding_text(
    *,
    base_text: str,
    chunk_type: ChunkType,
    section_path: list[str],
    content: str,
) -> str:
    table_metadata = extract_markdown_table_metadata(content)
    if chunk_type not in ENRICHED_CHUNK_TYPES and table_metadata is None:
        return base_text

    additions: list[str] = []
    label = chunk_type_label(chunk_type)

    if label is not None and f"Chunk type: {label}" not in base_text:
        additions.append(f"Chunk type: {label}")

    if section_path and (chunk_type in ENRICHED_CHUNK_TYPES or table_metadata is not None):
        local_title = section_path[-1]
        if f"Section: {local_title}" not in base_text:
            additions.append(f"Section: {local_title}")
        if len(section_path) >= 2:
            component = section_path[-2]
            if f"Component: {component}" not in base_text:
                additions.append(f"Component: {component}")

    if table_metadata is not None:
        _append_unique_prefixed_line(
            additions=additions,
            base_text=base_text,
            prefix="Table caption:",
            value=table_metadata.caption,
        )
        _append_unique_prefixed_line(
            additions=additions,
            base_text=base_text,
            prefix="Table context:",
            value=table_metadata.context,
        )
        _append_unique_prefixed_line(
            additions=additions,
            base_text=base_text,
            prefix="Table headers:",
            value=", ".join(table_metadata.headers) if table_metadata.headers else None,
        )
        _append_unique_prefixed_line(
            additions=additions,
            base_text=base_text,
            prefix="Row labels:",
            value=", ".join(table_metadata.row_labels) if table_metadata.row_labels else None,
        )
        _append_unique_prefixed_line(
            additions=additions,
            base_text=base_text,
            prefix="Units:",
            value=", ".join(table_metadata.units) if table_metadata.units else None,
        )

    aliases = build_chunk_related_terms(
        content=content,
        section_path=section_path,
        chunk_type=chunk_type,
    )
    if aliases and "Related terms:" not in base_text:
        alias_line = f"Related terms: {', '.join(aliases)}"
        additions.append(alias_line)

    if not additions:
        return base_text

    return base_text + "\n\n" + "\n\n".join(additions)


def _append_unique_prefixed_line(
    *,
    additions: list[str],
    base_text: str,
    prefix: str,
    value: str | None,
) -> None:
    if not value:
        return
    line = f"{prefix} {value}"
    if line in base_text:
        return
    additions.append(line)
