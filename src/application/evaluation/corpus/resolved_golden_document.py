from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from src.application.evaluation.corpus.golden_document_manifest_entry import (
    GoldenDocumentManifestEntry,
)


class GoldenDocumentAvailability(StrEnum):
    """Explicit outcome of resolving one manifest entry against the actual
    (externally/local-provisioned) corpus on disk. Never silently treated as
    "skip and move on" by a caller - see GoldenCorpusManifest.resolve_all()
    and the fast-regression runner's coverage reporting."""

    AVAILABLE = "available"
    MISSING = "missing"
    HASH_MISMATCH = "hash_mismatch"


@dataclass(slots=True, frozen=True)
class ResolvedGoldenDocument:
    entry: GoldenDocumentManifestEntry
    absolute_path: Path
    availability: GoldenDocumentAvailability
    actual_sha256: str | None = None

    @property
    def alias(self) -> str:
        return self.entry.alias

    @property
    def is_available(self) -> bool:
        return self.availability == GoldenDocumentAvailability.AVAILABLE


__all__ = ["GoldenDocumentAvailability", "ResolvedGoldenDocument"]
