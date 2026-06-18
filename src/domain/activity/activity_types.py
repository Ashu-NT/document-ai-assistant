from enum import Enum


class ActivitySeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ActivityStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"