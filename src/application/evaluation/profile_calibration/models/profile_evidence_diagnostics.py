from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProfileEvidenceDiagnostics:
    """Raw StructuralEvidenceSummary numbers for one profile, captured
    alongside a calibration case so a later multi-document analysis can
    relate score/outcome divergence back to the underlying evidence shape
    (matching_title_count/section_count coverage, distinct_term_count
    diversity) without re-parsing the document."""

    total_occurrences: int
    distinct_term_count: int
    matching_title_count: int
