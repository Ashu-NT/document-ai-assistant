from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChunkingProfileStatistics:
    element_count: int = 0
    section_count: int = 0
    root_section_count: int = 0
    nested_section_count: int = 0
    max_section_depth: int = 1

    table_count: int = 0
    picture_count: int = 0
    list_count: int = 0
    code_count: int = 0
    caption_count: int = 0
    text_element_count: int = 0
    text_token_total: int = 0
    long_text_block_count: int = 0
    short_text_block_count: int = 0

    avg_text_tokens: float = 0.0
    table_ratio: float = 0.0
    picture_ratio: float = 0.0
    list_ratio: float = 0.0
    code_ratio: float = 0.0
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

    def to_debug_dict(self) -> dict[str, int | float]:
        return {
            "element_count": self.element_count,
            "section_count": self.section_count,
            "root_section_count": self.root_section_count,
            "nested_section_count": self.nested_section_count,
            "max_section_depth": self.max_section_depth,
            "table_count": self.table_count,
            "picture_count": self.picture_count,
            "list_count": self.list_count,
            "code_count": self.code_count,
            "caption_count": self.caption_count,
            "text_element_count": self.text_element_count,
            "text_token_total": self.text_token_total,
            "long_text_block_count": self.long_text_block_count,
            "short_text_block_count": self.short_text_block_count,
            "avg_text_tokens": round(self.avg_text_tokens, 3),
            "table_ratio": round(self.table_ratio, 3),
            "picture_ratio": round(self.picture_ratio, 3),
            "list_ratio": round(self.list_ratio, 3),
            "code_ratio": round(self.code_ratio, 3),
            "caption_ratio": round(self.caption_ratio, 3),
            "nested_section_ratio": round(self.nested_section_ratio, 3),
            "long_text_ratio": round(self.long_text_ratio, 3),
            "short_text_ratio": round(self.short_text_ratio, 3),
            "manual_marker_hits": self.manual_marker_hits,
            "datasheet_marker_hits": self.datasheet_marker_hits,
            "drawing_marker_hits": self.drawing_marker_hits,
            "report_marker_hits": self.report_marker_hits,
            "certificate_marker_hits": self.certificate_marker_hits,
            "procedure_like_section_count": self.procedure_like_section_count,
        }
