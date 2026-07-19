from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerSource,
)

# Start narrow (PR 10, answering_flow_weakness_remediation_plan.md, W4):
# only these AnswerKeyValue.field_kind values are treated as
# contradiction-worthy -- specification/identifier already covers "part
# number" (KeyValueExtractor._field_kind() classifies part/serial/order/
# model numbers as "identifier"). Maintenance interval is handled
# separately below since it lives on AnswerMaintenanceEntry, not
# AnswerKeyValue. Procedure-step order is explicitly deferred -- detecting
# it needs a step-sequence parser this pass doesn't build (see PR 9's
# has_step_sequence_gap() for a narrower, answer-text-only version of that
# same idea).
_CONTRADICTION_FIELD_KINDS = frozenset({"identifier", "specification"})

_NUMBER_PATTERN = re.compile(r"[\d,]+(?:\.\d+)?")
_HOUR_UNIT_ALIASES = ("operating hours", "hours", "hrs", "hr", "h")
_PRESSURE_UNIT_ALIASES: dict[str, tuple[str, ...]] = {
    "bar": ("bar", "bars"),
    "psi": ("psi",),
}
_IDENTIFIER_PUNCTUATION_PATTERN = re.compile(r"[\s\-_.]+")
_WORD_PATTERN = re.compile(r"[a-z0-9]+")
_ARTICLES = frozenset({"the", "a", "an"})


@dataclass(frozen=True, slots=True)
class EvidenceConflict:
    """A key/task whose value disagrees across sources -- survives PR 10's
    unit/whitespace/decimal/punctuation normalization pass, so this is a
    genuine conflict, not a formatting difference ("1000 h" vs "1,000
    hours" vs "1000 operating hours" must never reach here). `is_critical`
    is a single tier for now (always True) -- graduated severity is PR 11's
    guardrail-severity model, not invented ahead of it here."""

    key: str
    field_kind: str
    values: tuple[str, ...]
    source_numbers: tuple[int, ...]
    is_critical: bool = True
    # Populated only when `detect()` is given `sources` (PR 11,
    # answering_flow_weakness_remediation_plan.md) -- lets a consumer (e.g.
    # ConflictingEvidenceGuardrail) distinguish "these sources genuinely
    # disagree" from "these sources describe different documents/equipment
    # and were never disambiguated" without doing its own source_number ->
    # document_id lookup. Empty when sources weren't provided.
    document_ids: tuple[str, ...] = ()


class EvidenceContradictionDetector:
    """Detects contradictions once, during evidence assembly (PR 10,
    answering_flow_weakness_remediation_plan.md, W4) -- reused by both the
    deterministic-renderer path (via DeterministicDispatchGate's
    CONFLICTING_EVIDENCE bypass) and the LLM path (which already knows to
    flag disagreement via its grounding rules), instead of building a
    second, parallel contradiction-flagging mechanism inside every
    renderer."""

    def detect(
        self,
        *,
        key_values: Sequence[AnswerKeyValue],
        maintenance_entries: Sequence[AnswerMaintenanceEntry],
        sources: Sequence[AnswerSource] | None = None,
    ) -> list[EvidenceConflict]:
        document_id_by_source_number = {
            source.source_number: source.document_id
            for source in (sources or [])
            if source.document_id
        }
        return [
            *self._detect_key_value_conflicts(key_values, document_id_by_source_number),
            *self._detect_maintenance_interval_conflicts(
                maintenance_entries, document_id_by_source_number
            ),
        ]

    def _detect_key_value_conflicts(
        self,
        key_values: Sequence[AnswerKeyValue],
        document_id_by_source_number: dict[int, str],
    ) -> list[EvidenceConflict]:
        groups: dict[str, dict[str, set[int]]] = {}
        raw_values: dict[tuple[str, str], str] = {}
        field_kind_by_key: dict[str, str] = {}
        for item in key_values:
            if item.field_kind not in _CONTRADICTION_FIELD_KINDS:
                continue
            normalized_key = _normalize_label(item.key)
            if not normalized_key:
                continue
            normalized_value = _normalize_conflict_value(
                value=item.value, unit=item.unit, field_kind=item.field_kind
            )
            if not normalized_value:
                continue
            groups.setdefault(normalized_key, {}).setdefault(
                normalized_value, set()
            ).add(item.source_number)
            raw_values[(normalized_key, normalized_value)] = item.value
            field_kind_by_key[normalized_key] = item.field_kind
        return [
            EvidenceConflict(
                key=key,
                field_kind=field_kind_by_key[key],
                values=tuple(
                    raw_values[(key, normalized_value)]
                    for normalized_value in value_groups
                ),
                source_numbers=tuple(sorted(all_sources)),
                document_ids=_document_ids_for(
                    all_sources, document_id_by_source_number
                ),
            )
            for key, value_groups, all_sources in self._conflicting_groups(groups)
        ]

    def _detect_maintenance_interval_conflicts(
        self,
        maintenance_entries: Sequence[AnswerMaintenanceEntry],
        document_id_by_source_number: dict[int, str],
    ) -> list[EvidenceConflict]:
        groups: dict[str, dict[str, set[int]]] = {}
        raw_values: dict[tuple[str, str], str] = {}
        for entry in maintenance_entries:
            normalized_task = _normalize_label(entry.task)
            normalized_interval = _normalize_conflict_value(
                value=entry.interval, unit=None, field_kind="maintenance_interval"
            )
            if not normalized_task or not normalized_interval:
                continue
            if normalized_interval == "not specified":
                continue
            groups.setdefault(normalized_task, {}).setdefault(
                normalized_interval, set()
            ).add(entry.source_number)
            raw_values[(normalized_task, normalized_interval)] = entry.interval
        return [
            EvidenceConflict(
                key=task,
                field_kind="maintenance_interval",
                values=tuple(
                    raw_values[(task, normalized_value)]
                    for normalized_value in value_groups
                ),
                source_numbers=tuple(sorted(all_sources)),
                document_ids=_document_ids_for(
                    all_sources, document_id_by_source_number
                ),
            )
            for task, value_groups, all_sources in self._conflicting_groups(groups)
        ]

    @staticmethod
    def _conflicting_groups(
        groups: dict[str, dict[str, set[int]]],
    ):
        for key, value_groups in groups.items():
            if len(value_groups) < 2:
                continue
            all_sources: set[int] = set()
            for sources in value_groups.values():
                all_sources |= sources
            # Distinct normalized values alone isn't enough -- if every
            # value traces back to the very same single source_number
            # (a messy multi-value extraction from one chunk), that's an
            # extraction quirk, not a cross-source disagreement.
            if len(all_sources) < 2:
                continue
            yield key, value_groups, all_sources


def _document_ids_for(
    source_numbers: set[int],
    document_id_by_source_number: dict[int, str],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                document_id_by_source_number[source_number]
                for source_number in source_numbers
                if source_number in document_id_by_source_number
            }
        )
    )


def _normalize_label(value: str) -> str:
    cleaned = " ".join(str(value or "").strip().lower().split())
    tokens = [
        token
        for token in _WORD_PATTERN.findall(cleaned)
        if token and token not in _ARTICLES
    ]
    return " ".join(tokens)


def _normalize_conflict_value(*, value: str, unit: str | None, field_kind: str) -> str:
    if field_kind == "identifier":
        return _IDENTIFIER_PUNCTUATION_PATTERN.sub("", str(value or "").strip().lower())
    return _normalize_measurement(value, unit)


def _normalize_measurement(value: str, unit: str | None) -> str:
    combined = f"{value or ''} {unit or ''}".strip().lower()
    combined = " ".join(combined.split())
    match = _NUMBER_PATTERN.search(combined)
    if match is None:
        return combined
    number = match.group(0).replace(",", "")
    remainder = combined[match.end():].strip()
    if any(alias in remainder for alias in _HOUR_UNIT_ALIASES):
        return f"{number} hours"
    for canonical, aliases in _PRESSURE_UNIT_ALIASES.items():
        if any(alias in remainder for alias in aliases):
            return f"{number} {canonical}"
    if not remainder:
        return number
    return f"{number} {remainder}"
