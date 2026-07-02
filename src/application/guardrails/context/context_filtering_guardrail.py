from __future__ import annotations

import re

from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
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


def _is_toc_chunk(chunk: RetrievedChunk) -> bool:
    text = chunk.content.strip()
    lower = text.lower()

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


def _is_branding_chunk(chunk: RetrievedChunk) -> bool:
    text = chunk.content.strip()
    lower = text.lower()

    if any(marker in lower for marker in _BRANDING_MARKERS):
        return True

    return False


def _is_noise_chunk(chunk: RetrievedChunk) -> bool:
    text = chunk.content.strip()
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
        if _is_toc_chunk(chunk):
            return GuardrailViolation(
                violation_type=ViolationType.TOC_CHUNK,
                message="Chunk is a table of contents entry.",
                chunk_id=chunk.chunk_id,
            )
        if _is_noise_chunk(chunk):
            return GuardrailViolation(
                violation_type=ViolationType.NOISE_CHUNK,
                message="Chunk is too short or contains only noise.",
                chunk_id=chunk.chunk_id,
            )
        if _is_branding_chunk(chunk):
            return GuardrailViolation(
                violation_type=ViolationType.BRANDING_CHUNK,
                message="Chunk contains only branding or copyright content.",
                chunk_id=chunk.chunk_id,
            )
        if (
            _is_maintenance_interval_query(query_text)
            and not _is_explicit_specification_query(query_text)
            and chunk.chunk_type == ChunkType.TECHNICAL_SPECIFICATION
            and not _has_maintenance_content(chunk.content)
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


def _has_maintenance_content(content: str) -> bool:
    normalized = content.lower()
    return any(marker in normalized for marker in _MAINTENANCE_CONTENT_MARKERS)
