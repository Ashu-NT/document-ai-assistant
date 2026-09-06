from enum import StrEnum


class HeadingCandidateRole(StrEnum):
    OUTLINE_SECTION = "outline_section"
    LOCAL_LABEL = "local_label"
    TABLE_CATEGORY = "table_category"
    CAPTION = "caption"
    NOISE = "noise"
