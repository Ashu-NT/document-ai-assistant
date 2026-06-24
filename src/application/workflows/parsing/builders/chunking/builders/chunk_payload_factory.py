from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.builders.chunk_type_resolver import (
    ChunkTypeResolver,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    common_path_prefix,
    unique_preserve_order,
)
from src.application.workflows.parsing.builders.chunking.text.section_path_sanitizer import (
    sanitize_section_path,
)
from src.domain.common import ChunkType

# Chunk types that benefit from richer embedding context (component, section title, aliases).
_ENRICHED_CHUNK_TYPES: frozenset[ChunkType] = frozenset(
    {ChunkType.MAINTENANCE_INTERVAL, ChunkType.TECHNICAL_SPECIFICATION}
)


def _maintenance_spec_aliases(*, content: str, section_path: list[str]) -> str | None:
    combined = " ".join([content] + section_path).lower()
    aliases: list[str] = []

    if any(k in combined for k in ("lubricat", "grease", "grease nipple", "shaft seal")):
        aliases.extend(
            ["lubrication interval", "greasing", "shaft seal lubrication", "grease schedule"]
        )

    if any(k in combined for k in ("oil quantit", "oil capacity", "oil volume", "oil fill", "fluid capacity")):
        aliases.extend(
            ["oil quantity", "oil specification", "fluid capacity", "oil fill quantity"]
        )

    if any(k in combined for k in ("oil change", "change interval", "replace oil", "renew oil", "drain screw")):
        aliases.extend(
            ["oil change interval", "oil replacement", "change frequency", "service interval"]
        )

    if any(k in combined for k in ("hours of operation", "every", "operating hours", "maintenance schedule", "lubrication schedule")):
        aliases.extend(
            ["maintenance interval", "service frequency", "operating hours", "scheduled maintenance"]
        )

    seen: set[str] = set()
    unique: list[str] = []
    for alias in aliases:
        if alias not in seen:
            seen.add(alias)
            unique.append(alias)
    return ", ".join(unique) if unique else None


class ChunkPayloadFactory:
    def __init__(
        self,
        *,
        chunk_type_resolver: ChunkTypeResolver | None = None,
    ) -> None:
        self.chunk_type_resolver = chunk_type_resolver or ChunkTypeResolver()

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
            document_title=document_title,
            section_path_lookup=section_path_lookup,
        )
        content = content_override or self._assemble_chunk_content(fragments)
        cleaned_content = clean_chunk_text(content) or ""
        chunk_type = self.chunk_type_resolver.resolve(
            fragments=fragments,
            content=cleaned_content,
        )

        return ChunkPayload(
            section_id=section_id,
            section_path=list(section_path),
            content=cleaned_content,
            chunk_type=chunk_type,
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
                chunk_type=chunk_type,
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

    def _resolve_payload_section(
        self,
        fragments: list[ChunkFragment],
        *,
        document_title: str | None,
        section_path_lookup: dict[tuple[str, ...], str] | None,
    ) -> tuple[str, list[str]]:
        section_paths = [
            sanitize_section_path(
                list(fragment.section_path),
                document_title=document_title,
            )
            for fragment in fragments
            if fragment.section_path
        ]
        common_path = common_path_prefix(section_paths)

        if common_path and section_path_lookup is not None:
            section_id = section_path_lookup.get(tuple(common_path))
            if section_id is not None:
                return section_id, common_path

        first_fragment = fragments[0]
        sanitized_first_path = sanitize_section_path(
            list(first_fragment.section_path),
            document_title=document_title,
        )
        return (
            first_fragment.section_id or "",
            sanitized_first_path,
        )

    @staticmethod
    def _build_embedding_text(
        *,
        document_title: str | None,
        section_path: list[str],
        content: str,
        chunk_type: ChunkType | None = None,
    ) -> str:
        parts: list[str] = []
        if document_title:
            parts.append(f"Document title: {document_title}")

        if section_path:
            parts.append(f"Section path: {' > '.join(section_path)}")
            if chunk_type in _ENRICHED_CHUNK_TYPES:
                local_title = section_path[-1]
                parts.append(f"Section: {local_title}")
                if len(section_path) >= 2:
                    parts.append(f"Component: {section_path[-2]}")

        parts.append(content)

        if chunk_type in _ENRICHED_CHUNK_TYPES:
            aliases = _maintenance_spec_aliases(content=content, section_path=section_path)
            if aliases:
                parts.append(f"Related terms: {aliases}")

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
