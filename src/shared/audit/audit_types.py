from enum import Enum


class AuditOutcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class AuditSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"