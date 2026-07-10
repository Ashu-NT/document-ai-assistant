from __future__ import annotations

# Section-path "is ancestor of" check -- previously reimplemented
# byte-identically four times: SectionChunkBuilder._is_path_prefix and
# ChunkPayloadSimilarityPolicy._is_path_prefix in the parsing/chunking
# subsystem, and RetrievalContextExpander._is_path_prefix and
# RetrievalDeduplicationPolicy._is_path_prefix in the retrieval subsystem.
# Consolidated here as the single shared primitive.


def is_path_prefix(
    ancestor_path: list[str],
    descendant_path: list[str],
) -> bool:
    if not ancestor_path or len(ancestor_path) > len(descendant_path):
        return False
    return descendant_path[: len(ancestor_path)] == ancestor_path
