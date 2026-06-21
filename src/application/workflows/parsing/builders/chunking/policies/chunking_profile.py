from enum import StrEnum


class ChunkingProfile(StrEnum):
    DEFAULT = "default"
    MANUAL = "manual"
    DATASHEET = "datasheet"
    DRAWING = "drawing"
    REPORT = "report"
    CERTIFICATE = "report"
