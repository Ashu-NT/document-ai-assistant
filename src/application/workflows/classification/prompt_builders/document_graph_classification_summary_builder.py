from collections import Counter

from src.domain.document import DocumentGraph


class DocumentGraphClassificationSummaryBuilder:
    def __init__(
        self,
        *,
        max_section_paths: int = 10,
        max_chunk_previews: int = 6,
        max_element_previews: int = 6,
        max_table_signals: int = 3,
        max_picture_signals: int = 3,
        preview_length: int = 240,
    ) -> None:
        self.max_section_paths = max_section_paths
        self.max_chunk_previews = max_chunk_previews
        self.max_element_previews = max_element_previews
        self.max_table_signals = max_table_signals
        self.max_picture_signals = max_picture_signals
        self.preview_length = preview_length

    def build(self, document_graph: DocumentGraph) -> str:
        lines: list[str] = []

        section_paths = self._section_paths(document_graph)
        if section_paths:
            lines.append("Representative section paths:")
            lines.extend(f"- {path}" for path in section_paths)

        element_type_counts = self._count_values(
            value.element_type.value
            for value in document_graph.elements.values()
        )
        if element_type_counts:
            lines.append("Element type distribution:")
            lines.extend(
                f"- {name}: {count}"
                for name, count in element_type_counts.items()
            )

        chunk_type_counts = self._count_values(
            value.chunk_type.value
            for value in document_graph.chunks.values()
        )
        if chunk_type_counts:
            lines.append("Chunk type distribution:")
            lines.extend(
                f"- {name}: {count}"
                for name, count in chunk_type_counts.items()
            )

        chunk_previews = self._chunk_previews(document_graph)
        if chunk_previews:
            lines.append("Representative chunk previews:")
            lines.extend(f"- {preview}" for preview in chunk_previews)
        else:
            element_previews = self._element_previews(document_graph)
            if element_previews:
                lines.append("Representative element previews:")
                lines.extend(f"- {preview}" for preview in element_previews)

        table_signals = self._table_signals(document_graph)
        if table_signals:
            lines.append("Table signals:")
            lines.extend(f"- {signal}" for signal in table_signals)

        picture_signals = self._picture_signals(document_graph)
        if picture_signals:
            lines.append("Picture signals:")
            lines.extend(f"- {signal}" for signal in picture_signals)

        if not lines:
            return "- No graph-derived content summary was available."

        return "\n".join(lines)

    def _section_paths(self, document_graph: DocumentGraph) -> list[str]:
        ordered_sections = sorted(
            document_graph.sections.values(),
            key=lambda value: value.sequence_number or 0,
        )
        unique_paths: list[str] = []
        seen_paths: set[str] = set()

        for section in ordered_sections:
            path_text = section.path_text().strip()
            if not path_text or path_text in seen_paths:
                continue
            seen_paths.add(path_text)
            unique_paths.append(path_text)
            if len(unique_paths) >= self.max_section_paths:
                break

        return unique_paths

    def _chunk_previews(self, document_graph: DocumentGraph) -> list[str]:
        ordered_chunks = sorted(
            (
                chunk
                for chunk in document_graph.chunks.values()
                if chunk.content and chunk.content.strip()
            ),
            key=lambda value: value.sequence_number or 0,
        )
        sampled_chunks = self._sample_evenly_spaced(
            ordered_chunks,
            self.max_chunk_previews,
        )
        previews: list[str] = []

        for chunk in sampled_chunks:
            section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"
            page_range = self._format_page_range(
                chunk.source.page_start,
                chunk.source.page_end,
            )
            previews.append(
                f"[{chunk.chunk_type.value}] {section_path} (pages {page_range}): "
                f"{self._preview_text(chunk.content)}"
            )

        return previews

    def _element_previews(self, document_graph: DocumentGraph) -> list[str]:
        ordered_elements = sorted(
            (
                element
                for element in document_graph.elements.values()
                if element.text and element.text.strip()
            ),
            key=lambda value: value.reading_order or 0,
        )
        sampled_elements = self._sample_evenly_spaced(
            ordered_elements,
            self.max_element_previews,
        )
        section_lookup = document_graph.sections
        previews: list[str] = []

        for element in sampled_elements:
            section = (
                section_lookup.get(element.parent_section_id)
                if element.parent_section_id
                else None
            )
            section_path = section.path_text() if section is not None else element.element_type.value
            page_range = self._format_page_range(
                element.source.page_start,
                element.source.page_end,
            )
            previews.append(
                f"{section_path} (pages {page_range}): "
                f"{self._preview_text(element.text or '')}"
            )

        return previews

    def _table_signals(self, document_graph: DocumentGraph) -> list[str]:
        signals: list[str] = []

        for table in list(document_graph.tables.values())[: self.max_table_signals]:
            caption = (table.metadata.caption or "").strip()
            content = table.markdown.strip()
            if caption:
                signals.append(
                    f"{caption}: {self._preview_text(content)}"
                )
            elif content:
                signals.append(self._preview_text(content))

        return signals

    def _picture_signals(self, document_graph: DocumentGraph) -> list[str]:
        signals: list[str] = []

        for picture in list(document_graph.pictures.values())[: self.max_picture_signals]:
            parts = [
                value.strip()
                for value in [
                    picture.metadata.caption or "",
                    picture.metadata.nearby_text or "",
                    picture.ocr_text or "",
                ]
                if value and value.strip()
            ]
            if not parts:
                continue
            signals.append(self._preview_text(" | ".join(parts)))

        return signals

    @staticmethod
    def _count_values(values: list[str] | tuple[str, ...] | object) -> dict[str, int]:
        counts = Counter(str(value) for value in values if str(value).strip())
        return dict(sorted(counts.items(), key=lambda item: item[0]))

    @staticmethod
    def _sample_evenly_spaced(values: list[object], max_items: int) -> list[object]:
        if len(values) <= max_items:
            return values

        max_index = len(values) - 1
        indexes = {
            round(position * max_index / (max_items - 1))
            for position in range(max_items)
        }
        return [values[index] for index in sorted(indexes)]

    def _preview_text(self, value: str) -> str:
        normalized = " ".join(value.split()).strip()
        if len(normalized) <= self.preview_length:
            return normalized
        return normalized[: self.preview_length - 3].rstrip() + "..."

    @staticmethod
    def _format_page_range(page_start: int | None, page_end: int | None) -> str:
        if page_start is None and page_end is None:
            return "N/A"
        if page_start == page_end:
            return str(page_start)
        if page_start is None:
            return str(page_end)
        if page_end is None:
            return str(page_start)
        return f"{page_start}-{page_end}"
