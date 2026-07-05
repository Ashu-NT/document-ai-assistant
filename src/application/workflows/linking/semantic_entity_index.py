from collections import defaultdict
from dataclasses import dataclass

from src.domain.extraction import SemanticEntityType, SemanticSourceMetadata


@dataclass(slots=True, frozen=True)
class IndexedEntity:
    """A single entity's locality signals, extracted from its
    `SemanticSourceMetadata`, for windowed relationship-candidate lookup."""

    entity_type: SemanticEntityType
    entity_id: str
    chunk_id: str | None
    section_id: str | None
    parent_section_id: str | None
    table_id: str | None
    page_start: int | None
    nearby_chunk_ids: tuple[str, ...]

    @classmethod
    def from_source_metadata(
        cls,
        entity_type: SemanticEntityType,
        entity_id: str,
        source_metadata: SemanticSourceMetadata | None,
    ) -> "IndexedEntity | None":
        if source_metadata is None:
            return None

        return cls(
            entity_type=entity_type,
            entity_id=entity_id,
            chunk_id=source_metadata.chunk_id,
            section_id=source_metadata.section_id,
            parent_section_id=source_metadata.parent_section_id,
            table_id=source_metadata.table_id,
            page_start=source_metadata.page_start,
            nearby_chunk_ids=source_metadata.nearby_chunk_ids,
        )


class SemanticEntityIndex:
    """Buckets entities by locality signal in a single O(n) pass so
    relationship-candidate generation only ever compares entities within a
    shared window (same table, chunk, section, parent section, or nearby
    chunk/page) instead of every pair in the document.
    """

    def __init__(self, entities: list[IndexedEntity]) -> None:
        self.entities = entities

        self.by_chunk: dict[str, list[IndexedEntity]] = defaultdict(list)
        self.by_section: dict[str, list[IndexedEntity]] = defaultdict(list)
        self.by_parent_section: dict[str, list[IndexedEntity]] = defaultdict(list)
        self.by_table: dict[str, list[IndexedEntity]] = defaultdict(list)

        for entity in entities:
            if entity.chunk_id:
                self.by_chunk[entity.chunk_id].append(entity)
            if entity.section_id:
                self.by_section[entity.section_id].append(entity)
            if entity.parent_section_id:
                self.by_parent_section[entity.parent_section_id].append(entity)
            if entity.table_id:
                self.by_table[entity.table_id].append(entity)

        self.sorted_by_page: list[IndexedEntity] = sorted(
            (entity for entity in entities if entity.page_start is not None),
            key=lambda entity: entity.page_start if entity.page_start is not None else 0,
        )
