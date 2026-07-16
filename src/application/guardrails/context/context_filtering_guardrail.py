from __future__ import annotations

import re

from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.workflows.shared.table_category import TableCategory
from src.domain.common import ChunkType
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

_TOC_MARKERS: frozenset[str] = frozenset(
    ["table of contents", "contents", "index", "inhaltsverzeichnis"]
)

_TOC_LINE_PATTERN = re.compile(
    r"^\s*(\d+\.)*\d*\s+.{3,60}\s*\.{2,}\s*\d+\s*$"
)

_BRANDING_MARKERS: frozenset[str] = frozenset(
    [
        "all rights reserved",
        "copyright ©",
        "© ",
        "proprietary and confidential",
        "www.",
        "http://",
        "https://",
    ]
)

_MIN_CONTENT_CHARS = 40
_TOC_LINE_DENSITY_THRESHOLD = 0.50
_MAINTENANCE_INTERVAL_QUERY_MARKERS: tuple[str, ...] = (
    "maintenance interval",
    "maintenance intervals",
    "service interval",
    "inspection interval",
    "maintenance schedule",
    "preventive maintenance",
)
_EXPLICIT_SPECIFICATION_QUERY_MARKERS: tuple[str, ...] = (
    "specification",
    "specifications",
    "technical data",
    "technical specification",
    "voltage",
    "power",
    "capacity",
    "speed",
    "dimensions",
    "model",
    "serial number",
    "pump type",
    "tank capacity",
)
_MAINTENANCE_CONTENT_MARKERS: tuple[str, ...] = (
    "maintenance",
    "interval",
    "service",
    "inspection",
    "operating hours",
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "annual",
    "annually",
    "lubrication",
    "preventive maintenance",
)
_SPARE_PARTS_QUERY_MARKERS: tuple[str, ...] = (
    "spare part",
    "spare parts",
)
_SPARE_PARTS_LIST_QUERY_MARKERS: tuple[str, ...] = (
    "list",
    "table",
)
_SPARE_PARTS_TABLE_CONTENT_MARKERS: tuple[str, ...] = (
    "position no",
    "pos.",
    "pos nr",
    "qty",
    "quantity",
    "designation",
    "denomination",
    "part no",
    "spare part no",
    "article no",
    "material no",
    "order no",
    "p&id",
    "service function",
)


def _is_toc_chunk(text: str, lower: str) -> bool:
    if any(marker in lower for marker in _TOC_MARKERS):
        return True

    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) >= 3:
        toc_line_count = sum(
            1 for line in lines if _TOC_LINE_PATTERN.match(line)
        )
        if toc_line_count / len(lines) >= _TOC_LINE_DENSITY_THRESHOLD:
            return True

    return False


def _is_branding_chunk(lower: str) -> bool:
    return any(marker in lower for marker in _BRANDING_MARKERS)


def _is_noise_chunk(text: str) -> bool:
    if not text:
        return True

    words = text.split()
    if len(words) < 5:
        return True

    if re.match(r"^\d+(\s*\|\s*\d+)*\s*$", text):
        return True

    return False


class ContextFilteringGuardrail:
    def check(self, context: GuardrailContext) -> GuardrailResult:
        chunks = context.retrieved_chunks
        if not chunks:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No chunks to filter.",
            )

        approved_ids: list[str] = []
        rejected_ids: list[str] = []
        violations: list[GuardrailViolation] = []

        for chunk in chunks:
            rejection = self._classify_chunk(chunk, query_text=context.query_text)
            if rejection is None:
                approved_ids.append(chunk.chunk_id)
            else:
                rejected_ids.append(chunk.chunk_id)
                violations.append(rejection)

        decision = GuardrailDecision.ALLOW if approved_ids else GuardrailDecision.INSUFFICIENT_EVIDENCE
        allowed = bool(approved_ids)
        reason = (
            f"{len(approved_ids)} chunk(s) approved, {len(rejected_ids)} filtered out."
        )

        return GuardrailResult(
            decision=decision,
            allowed=allowed,
            reason=reason,
            confidence=ConfidenceLevel.HIGH,
            violations=violations,
            evidence_summary=reason,
            approved_chunk_ids=approved_ids,
            rejected_chunk_ids=rejected_ids,
        )

    @staticmethod
    def _classify_chunk(
        chunk: RetrievedChunk,
        *,
        query_text: str,
    ) -> GuardrailViolation | None:
        text = chunk.content.strip()
        lower = text.lower()

        if _is_toc_chunk(text, lower):
            return GuardrailViolation(
                violation_type=ViolationType.TOC_CHUNK,
                message="Chunk is a table of contents entry.",
                chunk_id=chunk.chunk_id,
            )
        if _is_noise_chunk(text):
            return GuardrailViolation(
                violation_type=ViolationType.NOISE_CHUNK,
                message="Chunk is too short or contains only noise.",
                chunk_id=chunk.chunk_id,
            )
        if _is_branding_chunk(lower):
            return GuardrailViolation(
                violation_type=ViolationType.BRANDING_CHUNK,
                message="Chunk contains only branding or copyright content.",
                chunk_id=chunk.chunk_id,
            )
        if (
            _is_spare_parts_list_query(query_text)
            and chunk.chunk_type == ChunkType.SPARE_PARTS_TABLE
            and not _has_spare_parts_table_content(chunk, text, lower)
        ):
            return GuardrailViolation(
                violation_type=ViolationType.IRRELEVANT_CHUNKS,
                message=(
                    "Spare-parts chunk does not contain direct table/list evidence "
                    "for a spare-parts table request."
                ),
                chunk_id=chunk.chunk_id,
            )
        if (
            _is_maintenance_interval_query(query_text)
            and not _is_explicit_specification_query(query_text)
            and chunk.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
            and not _has_maintenance_content(lower)
        ):
            return GuardrailViolation(
                violation_type=ViolationType.IRRELEVANT_CHUNKS,
                message=(
                    "Technical specification chunk is off-intent for a maintenance "
                    "interval query."
                ),
                chunk_id=chunk.chunk_id,
            )
        return None


def _is_maintenance_interval_query(query_text: str) -> bool:
    normalized = query_text.lower()
    return any(marker in normalized for marker in _MAINTENANCE_INTERVAL_QUERY_MARKERS)


def _is_explicit_specification_query(query_text: str) -> bool:
    normalized = query_text.lower()
    return any(marker in normalized for marker in _EXPLICIT_SPECIFICATION_QUERY_MARKERS)


def _has_maintenance_content(lower: str) -> bool:
    return any(marker in lower for marker in _MAINTENANCE_CONTENT_MARKERS)


def _is_spare_parts_list_query(query_text: str) -> bool:
    normalized = query_text.lower()
    return any(marker in normalized for marker in _SPARE_PARTS_QUERY_MARKERS) and any(
        marker in normalized for marker in _SPARE_PARTS_LIST_QUERY_MARKERS
    )


def _has_spare_parts_table_content(
    chunk: RetrievedChunk,
    text: str,
    lower: str,
) -> bool:
    table_category = str(chunk.metadata.get("table_category", "")).strip().lower()
    if table_category == TableCategory.SPARE_PARTS_TABLE:
        return True
    if "|" not in text and not any(marker in lower for marker in _SPARE_PARTS_TABLE_CONTENT_MARKERS):
        return False
    has_marker = any(marker in lower for marker in _SPARE_PARTS_TABLE_CONTENT_MARKERS)
    has_digit = any(character.isdigit() for character in text)
    return has_marker and has_digit
