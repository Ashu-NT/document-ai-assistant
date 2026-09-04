from enum import StrEnum


class CrossReferenceReconciliationOutcome(StrEnum):
    """How a source_chunk_id's fuzzy/native cross-reference candidates were
    reconciled. Lives in its own module (rather than alongside
    ChunkCrossReference or CrossReferenceEvidence) because both of those
    entities reference it and neither should import the other."""

    # Only one source (fuzzy or native) produced a candidate for this chunk
    # - the overwhelming majority case, nothing to reconcile against.
    SINGLE_SOURCE = "single_source"
    # Fuzzy and native candidates agreed on the same target_chunk_id.
    CONFIRMED = "confirmed"
    # Candidates disagreed; an explicit SECTION_REFERENCE beat a conflicting
    # native link.
    ACCEPTED_TEXTUAL = "accepted_textual"
    # Candidates disagreed; a unique native link beat weak/heuristic fuzzy
    # evidence.
    ACCEPTED_NATIVE = "accepted_native"
    # Candidates disagreed and neither side is trusted over the other
    # (fuzzy PAGE_REFERENCE vs. native, both RESOLVED_UNIQUE) - no canonical
    # row is created for either.
    CONFLICT = "conflict"
    # Both sides had candidates for the same chunk but pairing which fuzzy
    # candidate corresponds to which native candidate is undecidable without
    # bbox/source-location matching (out of scope) - no canonical row is
    # created for any candidate in the group.
    UNRECONCILED_MULTI_CANDIDATE = "unreconciled_multi_candidate"


__all__ = ["CrossReferenceReconciliationOutcome"]
