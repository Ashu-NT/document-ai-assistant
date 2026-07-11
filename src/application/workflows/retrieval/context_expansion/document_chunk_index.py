from src.domain.common import ChunkType


class DocumentChunkIndex:
    """Pre-indexes one document's chunk list once so a per-anchor lookup
    only touches chunks that could plausibly match one of
    RetrievalContextExpander's relation types, instead of scanning every
    chunk in the document for every anchor. Each index is a superset lookup
    (it may occasionally include a chunk that the relation classifier
    ultimately rejects), never a subset -- the unchanged relation-checking
    logic is still the final word on whether a candidate actually
    qualifies."""

    def __init__(
        self,
        *,
        by_chunk_id: dict[str, object],
        by_section_id: dict[str, list],
        by_table_id: dict[str, list],
        by_picture_id: dict[str, list],
        overview_by_section_path: dict[tuple, list],
        by_section_path_prefix: dict[tuple, list],
        by_parent_path: dict[tuple, list],
        by_sequence_number: dict[int, list],
    ) -> None:
        self.by_chunk_id = by_chunk_id
        self.by_section_id = by_section_id
        self.by_table_id = by_table_id
        self.by_picture_id = by_picture_id
        self.overview_by_section_path = overview_by_section_path
        self.by_section_path_prefix = by_section_path_prefix
        self.by_parent_path = by_parent_path
        self.by_sequence_number = by_sequence_number

    @classmethod
    def build(cls, document_chunks: list) -> "DocumentChunkIndex":
        by_chunk_id: dict[str, object] = {}
        by_section_id: dict[str, list] = {}
        by_table_id: dict[str, list] = {}
        by_picture_id: dict[str, list] = {}
        overview_by_section_path: dict[tuple, list] = {}
        by_section_path_prefix: dict[tuple, list] = {}
        by_parent_path: dict[tuple, list] = {}
        by_sequence_number: dict[int, list] = {}

        for chunk in document_chunks:
            by_chunk_id[chunk.chunk_id] = chunk

            if chunk.section_id is not None:
                by_section_id.setdefault(chunk.section_id, []).append(chunk)

            for table_id in chunk.table_ids:
                by_table_id.setdefault(table_id, []).append(chunk)
            for picture_id in chunk.picture_ids:
                by_picture_id.setdefault(picture_id, []).append(chunk)

            path = tuple(chunk.section_path)
            if chunk.chunk_type == ChunkType.OVERVIEW:
                overview_by_section_path.setdefault(path, []).append(chunk)

            # Every proper prefix of this chunk's own path is a bucket it
            # belongs to, for the descendant-detail check: "chunks whose path
            # starts with the anchor's path" is answered by looking up the
            # anchor's own (exact) path in this index.
            for prefix_length in range(len(path)):
                by_section_path_prefix.setdefault(path[:prefix_length], []).append(chunk)

            if len(path) >= 1:
                by_parent_path.setdefault(path[:-1], []).append(chunk)

            by_sequence_number.setdefault(chunk.sequence_number, []).append(chunk)

        return cls(
            by_chunk_id=by_chunk_id,
            by_section_id=by_section_id,
            by_table_id=by_table_id,
            by_picture_id=by_picture_id,
            overview_by_section_path=overview_by_section_path,
            by_section_path_prefix=by_section_path_prefix,
            by_parent_path=by_parent_path,
            by_sequence_number=by_sequence_number,
        )

    def plausible_candidates(
        self,
        anchor_document_chunk,
        *,
        neighbor_window: int,
    ) -> list:
        candidates: dict[str, object] = {}

        def _add_all(chunks: list) -> None:
            for chunk in chunks:
                candidates[chunk.chunk_id] = chunk

        if anchor_document_chunk.section_id is not None:
            _add_all(self.by_section_id.get(anchor_document_chunk.section_id, []))

        anchor_path = tuple(anchor_document_chunk.section_path)
        for prefix_length in range(len(anchor_path)):
            _add_all(self.overview_by_section_path.get(anchor_path[:prefix_length], []))

        for table_id in anchor_document_chunk.table_ids:
            _add_all(self.by_table_id.get(table_id, []))
        for picture_id in anchor_document_chunk.picture_ids:
            _add_all(self.by_picture_id.get(picture_id, []))

        _add_all(self.by_section_path_prefix.get(anchor_path, []))

        if len(anchor_path) > 1:
            _add_all(self.by_parent_path.get(anchor_path[:-1], []))

        sequence_number = anchor_document_chunk.sequence_number
        for offset in range(-neighbor_window, neighbor_window + 1):
            if offset == 0:
                continue
            _add_all(self.by_sequence_number.get(sequence_number + offset, []))

        return list(candidates.values())
