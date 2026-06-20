from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    common_path_prefix,
    unique_preserve_order,
)
from src.domain.common import ChunkType


class ChunkPayloadFactory:
    def build_payload(
        self,
        *,
        document_title: str | None,
        fragments: list[ChunkFragment],
        content_override: str | None = None,
        section_path_lookup: dict[tuple[str, ...], str] | None = None,
    ) -> ChunkPayload:
        section_id, section_path = self._resolve_payload_section(
            fragments,
            section_path_lookup=section_path_lookup,
        )
        content = content_override or self._assemble_chunk_content(fragments)
        cleaned_content = clean_chunk_text(content) or ""

        return ChunkPayload(
            section_id=section_id,
            section_path=list(section_path),
            content=cleaned_content,
            chunk_type=self._resolve_chunk_type(fragments),
            element_ids=unique_preserve_order(
                element_id
                for fragment in fragments
                for element_id in fragment.element_ids
            ),
            table_ids=unique_preserve_order(
                table_id
                for fragment in fragments
                for table_id in fragment.table_ids
            ),
            picture_ids=unique_preserve_order(
                picture_id
                for fragment in fragments
                for picture_id in fragment.picture_ids
            ),
            page_start=self._min_fragment_page(fragments),
            page_end=self._max_fragment_page(fragments),
            embedding_text=self._build_embedding_text(
                document_title=document_title,
                section_path=section_path,
                content=cleaned_content,
            ),
        )

    def _assemble_chunk_content(
        self,
        fragments: list[ChunkFragment],
    ) -> str:
        parts: list[str] = []
        previous_path: list[str] = []

        for index, fragment in enumerate(fragments):
            if (
                index > 0
                and fragment.section_path
                and fragment.section_path != previous_path
                and fragment.section_title
            ):
                parts.append(fragment.section_title)

            if fragment.text:
                parts.append(fragment.text)

            previous_path = list(fragment.section_path)

        return "\n\n".join(part for part in parts if part).strip()

    @staticmethod
    def _resolve_chunk_type(fragments: list[ChunkFragment]) -> ChunkType:
        chunk_types = {
            fragment.chunk_type
            for fragment in fragments
        }
        if len(chunk_types) == 1:
            return next(iter(chunk_types))
        if chunk_types == {ChunkType.GENERAL, ChunkType.SPARE_PARTS_TABLE}:
            return ChunkType.GENERAL
        return ChunkType.GENERAL

    def _resolve_payload_section(
        self,
        fragments: list[ChunkFragment],
        *,
        section_path_lookup: dict[tuple[str, ...], str] | None,
    ) -> tuple[str, list[str]]:
        section_paths = [
            list(fragment.section_path)
            for fragment in fragments
            if fragment.section_path
        ]
        common_path = common_path_prefix(section_paths)

        if common_path and section_path_lookup is not None:
            section_id = section_path_lookup.get(tuple(common_path))
            if section_id is not None:
                return section_id, common_path

        first_fragment = fragments[0]
        return (
            first_fragment.section_id or "",
            list(first_fragment.section_path),
        )

    @staticmethod
    def _build_embedding_text(
        *,
        document_title: str | None,
        section_path: list[str],
        content: str,
    ) -> str:
        parts: list[str] = []
        if document_title:
            parts.append(f"Document title: {document_title}")

        if section_path:
            parts.append(f"Section path: {' > '.join(section_path)}")

        parts.append(content)
        return "\n\n".join(part for part in parts if part).strip()

    @staticmethod
    def _min_fragment_page(fragments: list[ChunkFragment]) -> int | None:
        pages = [
            fragment.page_start
            for fragment in fragments
            if fragment.page_start is not None
        ]
        return min(pages) if pages else None

    @staticmethod
    def _max_fragment_page(fragments: list[ChunkFragment]) -> int | None:
        pages = [
            fragment.page_end
            for fragment in fragments
            if fragment.page_end is not None
        ]
        return max(pages) if pages else None
