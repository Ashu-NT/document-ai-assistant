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

    manual_marker_hits: int = 0
    datasheet_marker_hits: int = 0
    drawing_marker_hits: int = 0
    report_marker_hits: int = 0
    certificate_marker_hits: int = 0
    procedure_like_section_count: int = 0

    @property
    def total_marker_hits(self) -> int:
        return (
            self.manual_marker_hits
            + self.datasheet_marker_hits
            + self.drawing_marker_hits
            + self.report_marker_hits
            + self.certificate_marker_hits
        )
