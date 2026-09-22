from dataclasses import dataclass

from src.domain.common import DocumentType


@dataclass(slots=True, frozen=True)
class GoldenDocumentManifestEntry:
    """Identity/inventory record for one golden evaluation document.

    Deliberately does NOT carry structural/extraction/retrieval expectations
    - those live in their own concern-specific sources (see
    outputs/architecture/golden_evaluation_corpus_architecture_investigation.md
    section 4). This is identity only: a stable alias, where the file is
    expected to live relative to the golden corpus root, and (where already
    human-reviewed) its expected production DocumentType.
    """

    alias: str
    relative_path: str
    # Free-form content-diversity label used only to organize the corpus
    # (e.g. "manual", "procedure_like") - NOT a production classification
    # value. `expected_document_type` below is the real production
    # DocumentType taxonomy; the two are intentionally decoupled (see
    # approved decision 2: do not force DocumentType to match this plan).
    category: str
    expected_document_type: DocumentType | None = None
    expected_sha256: str | None = None
    notes: str | None = None


__all__ = ["GoldenDocumentManifestEntry"]
