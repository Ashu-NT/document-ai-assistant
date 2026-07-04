from __future__ import annotations

from src.domain.document import DocumentChunk


def format_page_range(page_start: int | None, page_end: int | None) -> str:
    if page_start is None and page_end is None:
        return "N/A"
    if page_start == page_end:
        return str(page_start)
    if page_start is None:
        return str(page_end)
    if page_end is None:
        return str(page_start)
    return f"{page_start}-{page_end}"


def format_chunk_block(chunk: DocumentChunk) -> str:
    section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"
    page_range = format_page_range(chunk.source.page_start, chunk.source.page_end)

    return (
        f"- Chunk id: {chunk.chunk_id}\n"
        f"  Section path: {section_path}\n"
        f"  Source pages: {page_range}\n"
        f"  Chunk index: {chunk.chunk_index}/{chunk.chunk_total}\n"
        "  Content:\n"
        f"  {chunk.content}"
    )


def format_chunk_blocks(chunks: list[DocumentChunk]) -> str:
    return "\n\n".join(format_chunk_block(chunk) for chunk in chunks)


def allowed_chunk_ids(chunks: list[DocumentChunk]) -> str:
    return ", ".join(chunk.chunk_id for chunk in chunks)


def build_correction_notice(previous_error: str | None) -> str:
    if not previous_error:
        return ""

    return (
        "Your previous response was rejected because it did not match the "
        f"required schema: {previous_error}\n"
        "Fix this specific problem and return a corrected JSON response that "
        "matches the schema exactly.\n\n"
    )
