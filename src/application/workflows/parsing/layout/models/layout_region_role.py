from enum import StrEnum


class LayoutRegionRole(StrEnum):
    BODY_FLOW = "body_flow"
    FRONT_MATTER = "front_matter"
    FULL_WIDTH = "full_width"
    PARALLEL_COLUMN = "parallel_column"
    PICTURE_REGION = "picture_region"
    TABLE_REGION = "table_region"
