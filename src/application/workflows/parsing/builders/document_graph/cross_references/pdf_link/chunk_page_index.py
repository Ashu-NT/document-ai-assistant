from collections import defaultdict

from src.domain.document.entities.chunk import DocumentChunk


class ChunkPageIndex:
    """Maps each physical PDF page number to every chunk spanning that page,
    built once per document (same "build once" shape as
    ChunkSectionNumberIndex/ChunkAssetNumberIndex) so
    PdfLinkCrossReferenceLinker doesn't re-scan every chunk for each link
    annotation's source/dest page."""

    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self._chunks_by_page: dict[int, list[DocumentChunk]] = defaultdict(list)

        for chunk in chunks:
            page_start = chunk.source.page_start
            if page_start is None:
                continue
            page_end = chunk.source.page_end or page_start

            for page in range(page_start, page_end + 1):
                self._chunks_by_page[page].append(chunk)

    def chunks_for_page(self, page: int) -> list[DocumentChunk]:
        return list(self._chunks_by_page.get(page, ()))


__all__ = ["ChunkPageIndex"]
