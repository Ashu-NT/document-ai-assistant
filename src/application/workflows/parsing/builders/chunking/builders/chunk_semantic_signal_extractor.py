import re

from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.section_path_sanitizer import (
    sanitize_section_path,
)
from src.domain.common import ChunkType

_TITLE_MARKERS: dict[ChunkType, tuple[str, ...]] = {
    ChunkType.MAINTENANCE_PROCEDURE: (
        "maintenance procedure",
        "service procedure",
        "repair procedure",
        "replacement procedure",
        "procedure",
        "maintenance service",
    ),
    ChunkType.MAINTENANCE_INTERVAL: (
        "maintenance schedule",
        "service interval",
        "maintenance interval",
        "maintenance task",
        "inspection interval",
        "inspection schedule",
        "replacement interval",
        "lubrication schedule",
        "oil change interval",
    ),
    ChunkType.SAFETY_WARNING: (
        "safety",
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

_CONTENT_MARKERS: dict[ChunkType, tuple[str, ...]] = {
    ChunkType.MAINTENANCE_PROCEDURE: (
        "remove",
        "replace",
        "inspect",
        "tighten",
        "verify",
        "reinstall",
    ),
    ChunkType.SAFETY_WARNING: (
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
        "type",
        "specification",
        "year of manufacture",
        "flow rate",
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
    ),
    ChunkType.OPERATION_INSTRUCTION: (
        "operate",
        "turn on",
        "switch on",
        "start",
        "run",
        "press",
    ),
    ChunkType.CERTIFICATION_INFO: (
        "ce",
        "iec",
        "iso",
        "ul",
        "rohs",
    ),
}
_CONTENT_SCORE_CAPS: dict[ChunkType, int] = {
    ChunkType.TECHNICAL_SPECIFICATION: 4,
    ChunkType.TROUBLESHOOTING: 4,
}
_TABLE_CONTENT_MARKERS: dict[ChunkType, tuple[str, ...]] = {
    ChunkType.TECHNICAL_SPECIFICATION: (
        "serial number",
        "model number",
        "type",
        "drive type",
        "pump type",
        "press type",
        "year of manufacture",
        "specification",
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
_TABLE_SIGNAL_THRESHOLDS: dict[ChunkType, int] = {
    ChunkType.TECHNICAL_SPECIFICATION: 2,
    ChunkType.TROUBLESHOOTING: 2,
    ChunkType.OPERATION_INSTRUCTION: 3,
}

_INTERVAL_PATTERN = re.compile(
    r"\b(?:every\s+\d+(?:[.,]\d+)?\s+(?:hour|hours|day|days|week|weeks|month|months|year|years|cycle|cycles)"
    r"|daily|weekly|monthly|annually|yearly)\b",
    re.IGNORECASE,
)
_SPEC_VALUE_PATTERN = re.compile(
    r"\b(?:\d+(?:[.,]\d+)?\s?(?:v|kv|a|ma|hz|khz|mhz|ghz|w|kw|mm|cm|m|bar|psi|rpm|db|%)"
    r"|ip\d{2}|iec\s*\d+|iso\s*\d+|ce\b)\b",
    re.IGNORECASE,
)


class ChunkSemanticSignalExtractor:
    def extract_from_fragment(
        self,
        fragment: ChunkFragment,
    ) -> dict[ChunkType, int]:
        return self.extract(
            section_title=fragment.section_title,
            section_path=fragment.section_path,
            text=fragment.text,
            table_ids=fragment.table_ids,
        )

    def extract_from_fragments(
        self,
        fragments: list[ChunkFragment],
        *,
        content: str | None = None,
    ) -> dict[ChunkType, int]:
        if not fragments:
            return {}

        aggregated: dict[ChunkType, int] = {}
        for fragment in fragments:
            for chunk_type, score in self.extract_from_fragment(fragment).items():
                aggregated[chunk_type] = aggregated.get(chunk_type, 0) + score

        if content is not None:
            for chunk_type, score in self.extract(
                section_title=fragments[0].section_title,
                section_path=fragments[0].section_path,
                text=content,
                table_ids=[
                    table_id
                    for fragment in fragments
                    for table_id in fragment.table_ids
                ],
            ).items():
                aggregated[chunk_type] = aggregated.get(chunk_type, 0) + score

        return {
            chunk_type: score
            for chunk_type, score in aggregated.items()
            if score > 0
        }

    def extract(
        self,
        *,
        section_title: str | None,
        section_path: list[str],
        text: str | None,
        table_ids: list[str] | None = None,
    ) -> dict[ChunkType, int]:
        title_text = self._normalize_text(section_title)
        sanitized_path = sanitize_section_path(list(section_path))
        path_text = " > ".join(
            self._normalize_text(segment)
            for segment in sanitized_path
            if segment
        )
        content_text = self._normalize_text(text)
        scores: dict[ChunkType, int] = {}

        for chunk_type, markers in _TITLE_MARKERS.items():
            title_hits = self._marker_hits(title_text, markers)
            path_hits = self._marker_hits(path_text, markers)
            if title_hits:
                scores[chunk_type] = scores.get(chunk_type, 0) + (title_hits * 4)
            elif path_hits:
                scores[chunk_type] = scores.get(chunk_type, 0) + (path_hits * 3)

        for chunk_type, markers in _CONTENT_MARKERS.items():
            content_hits = self._marker_hits(content_text, markers)
            if content_hits:
                cap = _CONTENT_SCORE_CAPS.get(chunk_type, 2)
                scores[chunk_type] = scores.get(chunk_type, 0) + min(content_hits, 2)
                if cap != 2:
                    scores[chunk_type] = scores.get(chunk_type, 0) + (
                        min(content_hits, cap) - min(content_hits, 2)
                    )

        if _INTERVAL_PATTERN.search(content_text):
            scores[ChunkType.MAINTENANCE_INTERVAL] = (
                scores.get(ChunkType.MAINTENANCE_INTERVAL, 0) + 4
            )

        if _SPEC_VALUE_PATTERN.search(content_text):
            scores[ChunkType.TECHNICAL_SPECIFICATION] = (
                scores.get(ChunkType.TECHNICAL_SPECIFICATION, 0) + 2
            )

        if table_ids:
            scores[ChunkType.TECHNICAL_SPECIFICATION] = (
                scores.get(ChunkType.TECHNICAL_SPECIFICATION, 0) + 1
            )
            for chunk_type, bonus in self._table_signal_scores(content_text).items():
                scores[chunk_type] = scores.get(chunk_type, 0) + bonus

        return {
            chunk_type: score
            for chunk_type, score in scores.items()
            if score > 0
        }

    def _table_signal_scores(
        self,
        content_text: str,
    ) -> dict[ChunkType, int]:
        scores: dict[ChunkType, int] = {}
        for chunk_type, markers in _TABLE_CONTENT_MARKERS.items():
            marker_hits = self._marker_hits(content_text, markers)
            threshold = _TABLE_SIGNAL_THRESHOLDS.get(chunk_type, 2)
            if marker_hits < threshold:
                continue
            scores[chunk_type] = min(marker_hits + 1, 5)
        return scores

    @staticmethod
    def _marker_hits(text: str, markers: tuple[str, ...]) -> int:
        if not text:
            return 0

        return sum(1 for marker in markers if marker in text)

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""
        normalized = re.sub(r"[\W_]+", " ", value, flags=re.UNICODE)
        return re.sub(r"\s+", " ", normalized).strip().lower()
