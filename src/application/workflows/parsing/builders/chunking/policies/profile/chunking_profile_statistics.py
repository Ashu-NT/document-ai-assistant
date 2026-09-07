from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChunkingProfileStatistics:
    element_count: int = 0
    section_count: int = 0
    root_section_count: int = 0
    nested_section_count: int = 0
    max_section_depth: int = 1

    text_element_count: int = 0

    avg_text_tokens: float = 0.0
    table_ratio: float = 0.0
    picture_ratio: float = 0.0
    list_ratio: float = 0.0
    caption_ratio: float = 0.0
    nested_section_ratio: float = 0.0
    long_text_ratio: float = 0.0
    short_text_ratio: float = 0.0

    # Counts of profile-indicative terms found in section/document TITLES (a
    # crude substring search, see ChunkingProfileStatisticsBuilder) feeding
    # the "structural_evidence" signal used by
    # ChunkingProfileInferer/HybridDocumentTypeResolver -- deliberately named
    # "structural_evidence", not "marker", so this isn't confused with the
    # unrelated, much richer EvidenceMarker/MarkerStrength system under
    # chunking/builders/structured/markers, which scores evidence within
    # already-classified section content, not raw title term density across
    # a whole document.
    manual_structural_evidence_hits: int = 0
    datasheet_structural_evidence_hits: int = 0
    drawing_structural_evidence_hits: int = 0
    report_structural_evidence_hits: int = 0
    certificate_structural_evidence_hits: int = 0
    procedure_like_section_count: int = 0

    @property
    def total_structural_evidence_hits(self) -> int:
        return (
            self.manual_structural_evidence_hits
            + self.datasheet_structural_evidence_hits
            + self.drawing_structural_evidence_hits
            + self.report_structural_evidence_hits
            + self.certificate_structural_evidence_hits
        )
