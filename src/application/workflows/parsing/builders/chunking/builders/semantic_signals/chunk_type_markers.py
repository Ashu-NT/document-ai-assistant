import re

from src.application.workflows.parsing.builders.chunking.text.text_normalization import (
    normalize_comparable_text,
)
from src.domain.common import ChunkType

# `marker_hits` lives in this (data-only) module rather than in the extractor
# or the table-signal scorer so both of those files can import it from one
# leaf module without creating a circular import between them.


def marker_hits(text: str, markers: tuple[str, ...]) -> int:
    if not text or not markers:
        return 0

    padded_text = f" {text} "
    hits = 0
    for marker in markers:
        if f" {marker} " in padded_text:
            hits += 1
    return hits


def _normalize_marker_map(
    marker_map: dict[ChunkType, tuple[str, ...]],
) -> dict[ChunkType, tuple[str, ...]]:
    normalized_map: dict[ChunkType, tuple[str, ...]] = {}
    for chunk_type, markers in marker_map.items():
        normalized_markers = tuple(
            normalized_marker
            for marker in markers
            if (normalized_marker := normalize_comparable_text(marker))
        )
        normalized_map[chunk_type] = normalized_markers
    return normalized_map


TITLE_MARKERS: dict[ChunkType, tuple[str, ...]] = {
    ChunkType.MAINTENANCE_PROCEDURE: (
        "maintenance procedure",
        "service procedure",
        "repair procedure",
        "replacement procedure",
        "procedure",
        "maintenance service",
    ),
    ChunkType.MAINTENANCE_INTERVAL: (
        "maintenance table",
        "maintenance schedule",
        "service interval",
        "maintenance interval",
        "maintenance task",
        "service life",
        "inspection interval",
        "inspection schedule",
        "replacement intervals",
        "replacement interval",
        "lubrication schedule",
        "oil change interval",
        "frequency",
    ),
    ChunkType.SAFETY_WARNING: (
        "safety",
        "alarm condition",
        "alarm conditions",
        "warning condition",
        "warning conditions",
        "warning",
        "warnings",
        "caution",
        "danger",
        "hazard",
        "precaution",
    ),
    ChunkType.TROUBLESHOOTING: (
        "troubleshooting",
        "trouble shooting",
        "does not start",
        "will not start",
        "no sound",
        "no discharge",
        "low flow",
        "leakage",
        "leaking",
        "fault",
        "faults",
        "diagnostic",
        "diagnostics",
        "problem",
        "problems",
        "error",
        "errors",
        "symptom",
        "symptoms",
    ),
    ChunkType.TECHNICAL_SPECIFICATION: (
        "technical data",
        "technical specification",
        "technical specifications",
        "specification",
        "specifications",
        "electrical specification",
        "electrical specifications",
        "ratings",
        "parameters",
        "dimensions",
    ),
    ChunkType.INSTALLATION_INSTRUCTION: (
        "installation",
        "electrical connection",
        "pneumatic connection",
        "mounting",
        "assembly",
        "commissioning",
        "setup",
    ),
    ChunkType.OPERATION_INSTRUCTION: (
        "operation",
        "operating",
        "startup",
        "start-up",
        "shutdown",
        "usage",
        "how to use",
        "connecting the device",
    ),
    ChunkType.CERTIFICATION_INFO: (
        "certificate",
        "certification",
        "compliance",
        "conformity",
        "regulatory",
        "standards",
        "standard",
        "atex",
        "iecex",
        "approval",
    ),
}

CONTENT_MARKERS: dict[ChunkType, tuple[str, ...]] = {
    ChunkType.MAINTENANCE_PROCEDURE: (
        "remove",
        "replace",
        "inspect",
        "tighten",
        "verify",
        "reinstall",
    ),
    ChunkType.MAINTENANCE_INTERVAL: (
        "maintenance table",
        "maintenance interval",
        "maintenance intervals",
        "maintenance schedule",
        "service interval",
        "inspection interval",
        "change interval",
        "preventive maintenance",
        "daily use",
        "operating hours",
        "running hours",
        "service life",
        "frequency",
        "wear replacement",
    ),
    ChunkType.SAFETY_WARNING: (
        "alarm condition",
        "alarm conditions",
        "warning condition",
        "warning conditions",
        "alarm relay",
        "red alarm lamp",
        "fault lamp",
        "shut down immediately",
        "warning",
        "caution",
        "danger",
        "hazard",
        "disconnect power",
        "wear gloves",
        "protective equipment",
    ),
    ChunkType.TROUBLESHOOTING: (
        "probable cause",
        "probable causes",
        "possible cause",
        "possible causes",
        "possible problem",
        "possible problems",
        "possible remedy",
        "possible remedies",
        "potential remedy",
        "potential remedies",
        "corrective action",
        "no sound",
        "no discharge",
        "low flow",
        "leakage",
        "leaking",
        "if the",
        "not working",
        "fails to",
        "check whether",
    ),
    ChunkType.TECHNICAL_SPECIFICATION: (
        "serial number",
        "model number",
        "part number",
        "drawing number",
        "order code",
        "order number",
        "press type",
        "drive type",
        "specification",
        "year of manufacture",
        "flow rate",
        "oil quantity",
        "change interval",
        "operating pressure",
        "supply voltage",
        "power",
        "rpm",
        "material",
        "nominal size",
    ),
    ChunkType.INSTALLATION_INSTRUCTION: (
        "install",
        "mount",
        "attach",
        "secure",
        "align",
        "electrical connection",
        "pneumatic connection",
        "wiring",
    ),
    ChunkType.OPERATION_INSTRUCTION: (
        "operate",
        "turn on",
        "switch on",
        "start",
        "run",
        "press",
        "connect the device",
        "connect according to diagram",
        "check supply voltage",
        "switch off supply voltage",
    ),
    ChunkType.CERTIFICATION_INFO: (
        "ce conformity",
        "ce declaration",
        "ce marking",
        "iec",
        "iso",
        "ul listed",
        "rohs",
    ),
}
CONTENT_SCORE_CAPS: dict[ChunkType, int] = {
    ChunkType.MAINTENANCE_INTERVAL: 4,
    ChunkType.TECHNICAL_SPECIFICATION: 4,
    ChunkType.TROUBLESHOOTING: 4,
}
TABLE_CONTENT_MARKERS: dict[ChunkType, tuple[str, ...]] = {
    ChunkType.MAINTENANCE_INTERVAL: (
        "maintenance interval",
        "maintenance intervals",
        "maintenance schedule",
        "maintenance table",
        "service interval",
        "replacement interval",
        "replacement intervals",
        "operating hours",
        "running hours",
        "service life",
        "frequency",
        "task",
        "tasks",
        "interval",
        "done",
        "comments",
    ),
    ChunkType.TECHNICAL_SPECIFICATION: (
        "serial number",
        "model number",
        "order code",
        "drive type",
        "pump type",
        "press type",
        "year of manufacture",
        "specification",
        "oil quantity",
        "change interval",
        "flow rate",
        "operating pressure",
        "supply voltage",
        "power",
        "rpm",
        "material",
        "nominal size",
    ),
    ChunkType.TROUBLESHOOTING: (
        "problem",
        "problems",
        "possible cause",
        "possible causes",
        "probable cause",
        "probable causes",
        "possible remedy",
        "possible remedies",
        "potential remedy",
        "potential remedies",
        "corrective action",
        "remedy",
    ),
    ChunkType.OPERATION_INSTRUCTION: (
        "operating element",
        "control element",
        "operating key",
        "function",
        "display",
        "indicator",
    ),
}
TABLE_SIGNAL_THRESHOLDS: dict[ChunkType, int] = {
    ChunkType.MAINTENANCE_INTERVAL: 2,
    ChunkType.TECHNICAL_SPECIFICATION: 2,
    ChunkType.TROUBLESHOOTING: 2,
    ChunkType.OPERATION_INSTRUCTION: 3,
}
NORMALIZED_TITLE_MARKERS = _normalize_marker_map(TITLE_MARKERS)
NORMALIZED_CONTENT_MARKERS = _normalize_marker_map(CONTENT_MARKERS)
NORMALIZED_TABLE_CONTENT_MARKERS = _normalize_marker_map(TABLE_CONTENT_MARKERS)

INTERVAL_PATTERN = re.compile(
    r"\b(?:every\s+\d+(?:[.,]\d+)?\s+(?:hour|hours|day|days|week|weeks|month|months|year|years|cycle|cycles)"
    r"|daily|weekly|monthly|annually|yearly)\b",
    re.IGNORECASE,
)
SPEC_VALUE_PATTERN = re.compile(
    r"\b(?:\d+(?:[.,]\d+)?\s?(?:v|kv|a|ma|hz|khz|mhz|ghz|w|kw|mm|cm|m|bar|psi|rpm|db|%)"
    r"|ip\d{2}|iec\s*\d+|iso\s*\d+|ce\b)\b",
    re.IGNORECASE,
)
