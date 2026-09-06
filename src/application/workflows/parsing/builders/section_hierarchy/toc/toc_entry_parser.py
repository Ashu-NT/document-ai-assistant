import re

from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    numbering_depth,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry import (
    TocEntry,
    normalize_toc_title,
)
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement


class TocEntryParser:
    """Parses raw TOC table rows or text blocks into `TocEntry` records."""

    @staticmethod
    def extract_entries_from_element(element: ParsedCanonicalElement) -> list[TocEntry]:
        parallel_streams = element.metadata.get("table_parallel_stream_rows")
        if isinstance(parallel_streams, list):
            entries: list[TocEntry] = []
            for stream_rows in parallel_streams:
                if isinstance(stream_rows, list):
                    entries.extend(TocEntryParser.parse_toc_rows(stream_rows))
            if entries:
                return entries

        rows = element.metadata.get("table_rows")
        if isinstance(rows, list):
            entries = TocEntryParser.parse_toc_rows(rows)
            if entries:
                return entries

        text = element.text or element.metadata.get("markdown")
        if not text:
            return []

        return TocEntryParser.parse_toc_text(text)

    @staticmethod
    def parse_toc_rows(rows: list[object]) -> list[TocEntry]:
        entries: list[TocEntry] = []
        for row in rows:
            if not isinstance(row, list):
                continue

            cells = [TocEntryParser._clean_cell(cell) for cell in row]
            if not any(cells):
                continue

            page_index, page_no = TocEntryParser._extract_row_page(cells)
            if page_index is None or page_no is None:
                continue

            content_cells = [
                cell
                for index, cell in enumerate(cells)
                if index != page_index and cell
            ]
            if not content_cells:
                continue

            numbering: str | None = None
            title_parts: list[str] = []
            for cell in content_cells:
                exact_number = TocEntryParser._extract_exact_number(cell)
                if exact_number is not None and numbering is None:
                    numbering = exact_number
                    continue

                combined_number, combined_title = TocEntryParser._split_number_and_title(cell)
                if combined_number is not None and numbering is None:
                    numbering = combined_number
                    if combined_title:
                        title_parts.append(combined_title)
                    continue

                title_parts.append(cell)

            title = TocEntryParser._clean_toc_title(
                " ".join(TocEntryParser._dedupe_consecutive(title_parts))
            )
            if not title:
                continue

            level_hint = numbering_depth(numbering)
            if level_hint is None:
                first_content_index = min(
                    index
                    for index, cell in enumerate(cells)
                    if cell and index != page_index
                )
                level_hint = max(1, first_content_index + 1)

            entries.append(
                TocEntry(
                    title=title,
                    normalized_title=normalize_toc_title(title),
                    start_page=page_no,
                    level_hint=level_hint,
                    numbering=numbering,
                )
            )

        return entries

    @staticmethod
    def parse_toc_text(text: str) -> list[TocEntry]:
        entries: list[TocEntry] = []
        for raw_line in text.splitlines():
            line = raw_line.strip().strip("|").strip()
            if not line or set(line) <= {"-", ":", "|"}:
                continue

            line = repair_docling_text(line)
            line = re.sub(r"\s+", " ", line)
            match = re.match(r"^(?P<title>.+?)\.{2,}\s*(?P<page>\d+)$", line)
            if match is None:
                match = re.match(r"^(?P<title>.+?)\s+(?P<page>\d+)$", line)
            if match is None:
                continue

            title_text = TocEntryParser._clean_toc_title(match.group("title"))
            if not title_text:
                continue

            numbering, title = TocEntryParser._split_number_and_title(title_text)
            normalized_title = normalize_toc_title(title or title_text)
            if not normalized_title:
                continue

            entries.append(
                TocEntry(
                    title=title or title_text,
                    normalized_title=normalized_title,
                    start_page=int(match.group("page")),
                    level_hint=numbering_depth(numbering) or 1,
                    numbering=numbering,
                )
            )

        return entries

    @staticmethod
    def _extract_row_page(cells: list[str]) -> tuple[int | None, int | None]:
        for index in range(len(cells) - 1, -1, -1):
            cell = cells[index]
            if not cell:
                continue

            if re.fullmatch(r"\d{1,4}", cell):
                return index, int(cell)

        return None, None

    @staticmethod
    def _extract_exact_number(value: str) -> str | None:
        match = re.fullmatch(r"(\d+(?:\.\d+)*)", value.strip())
        if match is None:
            return None

        return match.group(1)

    @staticmethod
    def _split_number_and_title(value: str) -> tuple[str | None, str | None]:
        stripped = value.strip()
        match = re.match(
            r"^(?P<number>\d+(?:\.\d+)*)\s+(?P<title>.+)$",
            stripped,
        )
        if match is None:
            return None, stripped or None

        return match.group("number"), match.group("title").strip(" .")

    @staticmethod
    def _clean_cell(value: object) -> str:
        return re.sub(r"\s+", " ", repair_docling_text(str(value or "")).strip())

    @staticmethod
    def _dedupe_consecutive(values: list[str]) -> list[str]:
        deduped: list[str] = []
        for value in values:
            if not value:
                continue
            if deduped and deduped[-1] == value:
                continue
            deduped.append(value)
        return deduped

    @staticmethod
    def _clean_toc_title(value: str | None) -> str:
        if not value:
            return ""

        text = repair_docling_text(value)
        text = re.sub(r"\.{2,}", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip(" .|-")
