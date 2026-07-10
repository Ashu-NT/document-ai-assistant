from __future__ import annotations

from typing import Any

# "Coerce to a positive int, else None" -- previously reimplemented
# byte-identically in ChunkFragmentBuilder._coerce_positive_int,
# SectionHierarchyResolver._coerce_positive_int, and
# DoclingDocumentNormalizer._coerce_positive_int. Consolidated here as the
# single shared primitive for the parsing/chunking subsystem.


def coerce_positive_int(value: Any) -> int | None:
    if value is None:
        return None

    try:
        number = int(value)
    except (TypeError, ValueError):
        return None

    return number if number > 0 else None
