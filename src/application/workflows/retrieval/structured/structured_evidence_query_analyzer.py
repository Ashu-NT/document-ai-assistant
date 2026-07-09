from __future__ import annotations

# Keyword-taxonomy-sprawl note (deliberate, not an oversight): this module's
# _MANUFACTURER_TERMS/_SPECIFICATION_TERMS/_MAINTENANCE_TERMS/etc. are yet
# another independent marker-list taxonomy, joining RetrievalQueryIntent's,
# AnswerIntent's, the strategy-advisor's, the guardrail's, the reflection
# validator's, and the deterministic planner's -- each catalogued separately
# during this codebase's intent-hardening pass. It is intentionally NOT
# merged into any of those: each taxonomy answers a different question
# (retrieval routing vs. answer formatting vs. structured-entity-type
# selection) over a different value space (RetrievalQueryIntent enum members
# vs. StructuredEntityType enum members here), so a shared vocabulary would
# need a lossy translation layer between enums that don't correspond 1:1
# rather than removing real duplication. Precedent from that pass: only
# consolidate when two lists drift on the SAME narrow concept (e.g. the
# identifier-inventory regex/marker duplication fixed alongside this note,
# see identifier_value_pattern.py) -- not force unrelated taxonomies
# together because they're superficially similar in shape.
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.structured.structured_entity_type import (
    StructuredEntityType,
)
from src.application.workflows.retrieval.structured.structured_evidence_query_analysis import (
    StructuredEvidenceQueryAnalysis,
)
from src.application.workflows.retrieval.structured.structured_identifier_query_analyzer import (
    StructuredIdentifierQueryAnalyzer,
)

_DETAIL_TERMS = (
    "website",
    "url",
    "email",
    "e-mail",
    "phone",
    "telephone",
    "fax",
    "contact",
    "country",
    "based in",
    "located",
    "quantity",
    "how many",
    "in stock",
    "interval",
    "how often",
)
_CONTACT_DETAIL_TERMS = ("email", "e-mail", "phone", "telephone", "fax", "contact")
_WEBSITE_TERMS = ("website", "url", "web address")
_COUNTRY_TERMS = ("country", "based in", "located")
_MANUFACTURER_TERMS = ("manufacturer", "made by", "manufactured by")
_SUPPLIER_TERMS = ("supplier", "vendor", "distributor")
_SPARE_PART_TERMS = ("spare part", "spare parts")
_EQUIPMENT_TERMS = ("equipment", "system", "pump", "press", "collector", "device")
_SPECIFICATION_TERMS = (
    "specification",
    "specifications",
    "spec",
    "specs",
    "technical data",
    "technical specification",
    "pressure",
    "temperature",
    "voltage",
    "power",
    "capacity",
    "rating",
    "dimension",
    "material",
    "serial number",
    "model number",
)
_MAINTENANCE_TERMS = (
    "maintenance",
    "maintenance task",
    "maintenance tasks",
    "service interval",
    "service schedule",
    "preventive maintenance",
    "lubrication",
    "inspection",
)
_MAINTENANCE_INTERVAL_TERMS = (
    "maintenance interval",
    "maintenance intervals",
    "service interval",
    "service intervals",
    "schedule",
    "how often",
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "annual",
    "annually",
)
_PROCEDURE_TERMS = (
    "procedure",
    "procedures",
    "how to",
    "steps",
    "install",
    "replace",
    "remove",
    "start",
    "stop",
    "commission",
    "operate",
)
_TROUBLESHOOTING_TERMS = (
    "troubleshooting",
    "troubleshoot",
    "fault",
    "error",
    "problem",
    "cause",
    "remedy",
)
_SAFETY_TERMS = ("safety", "warning", "warnings", "hazard", "caution")


class StructuredEvidenceQueryAnalyzer:
    def __init__(
        self,
        *,
        identifier_query_analyzer: StructuredIdentifierQueryAnalyzer | None = None,
    ) -> None:
        self.identifier_query_analyzer = (
            identifier_query_analyzer or StructuredIdentifierQueryAnalyzer()
        )

    def analyze(
        self,
        *,
        query_text: str,
        intent: str | None = None,
        detected_identifiers: list[str] | None = None,
    ) -> StructuredEvidenceQueryAnalysis:
        normalized = " ".join((query_text or "").strip().lower().split())
        detail_entity_type = self._detail_entity_type(normalized)
        entity_types: list[StructuredEntityType] = []

        if detail_entity_type is not None:
            entity_types.append(detail_entity_type)
            if (
                detail_entity_type in {
                    StructuredEntityType.MANUFACTURER,
                    StructuredEntityType.SUPPLIER,
                }
                and any(term in normalized for term in _CONTACT_DETAIL_TERMS)
            ):
                entity_types.append(StructuredEntityType.CONTACT_POINT)

        if any(term in normalized for term in _MANUFACTURER_TERMS):
            entity_types.append(StructuredEntityType.MANUFACTURER)
        if any(term in normalized for term in _SUPPLIER_TERMS):
            entity_types.append(StructuredEntityType.SUPPLIER)
        if any(term in normalized for term in _SPARE_PART_TERMS):
            entity_types.append(StructuredEntityType.SPARE_PART)
        if any(term in normalized for term in _EQUIPMENT_TERMS):
            entity_types.append(StructuredEntityType.EQUIPMENT)
        if any(term in normalized for term in _SPECIFICATION_TERMS):
            entity_types.extend(
                [
                    StructuredEntityType.SPECIFICATION,
                    StructuredEntityType.EQUIPMENT,
                ]
            )
        if any(term in normalized for term in _MAINTENANCE_INTERVAL_TERMS):
            entity_types.extend(
                [
                    StructuredEntityType.MAINTENANCE_INTERVAL,
                    StructuredEntityType.MAINTENANCE_TASK,
                ]
            )
        elif any(term in normalized for term in _MAINTENANCE_TERMS):
            entity_types.extend(
                [
                    StructuredEntityType.MAINTENANCE_TASK,
                    StructuredEntityType.PROCEDURE,
                ]
            )
        if any(term in normalized for term in _PROCEDURE_TERMS):
            entity_types.append(StructuredEntityType.PROCEDURE)
        if any(term in normalized for term in _TROUBLESHOOTING_TERMS):
            entity_types.append(StructuredEntityType.TROUBLESHOOTING)
        if any(term in normalized for term in _SAFETY_TERMS):
            entity_types.append(StructuredEntityType.SAFETY_WARNING)

        # Compared against RetrievalQueryIntent's own enum values (not bare
        # string literals) so a rename/typo fails loudly instead of silently
        # becoming an unreachable branch -- caught one exactly that shape:
        # an `elif intent == "certification":` branch here that could never
        # match, since RetrievalQueryIntent has no CERTIFICATION member (that
        # name only exists on the unrelated AnswerIntent enum). Removed
        # rather than "fixed" -- there's no keyword-driven certification
        # signal elsewhere in this analyzer to hang a real implementation
        # off of; certification-relevant entities are already reachable via
        # the _SPECIFICATION_TERMS keyword bucket above.
        if intent == RetrievalQueryIntent.MAINTENANCE.value:
            entity_types.extend(
                [
                    StructuredEntityType.MAINTENANCE_TASK,
                    StructuredEntityType.MAINTENANCE_INTERVAL,
                    StructuredEntityType.PROCEDURE,
                ]
            )
        elif intent == RetrievalQueryIntent.PROCEDURE.value:
            entity_types.append(StructuredEntityType.PROCEDURE)
        elif intent == RetrievalQueryIntent.TROUBLESHOOTING.value:
            entity_types.append(StructuredEntityType.TROUBLESHOOTING)
        elif intent == RetrievalQueryIntent.SPECIFICATION.value:
            entity_types.extend(
                [
                    StructuredEntityType.SPECIFICATION,
                    StructuredEntityType.EQUIPMENT,
                ]
            )

        if detected_identifiers:
            entity_types.extend(
                [
                    StructuredEntityType.SPARE_PART,
                    StructuredEntityType.EQUIPMENT,
                    StructuredEntityType.SPECIFICATION,
                ]
            )

        return StructuredEvidenceQueryAnalysis(
            entity_types=self._ordered_unique(entity_types),
            identifier_types=self.identifier_query_analyzer.requested_identifier_types(
                normalized
            ),
            detail_entity_type=detail_entity_type,
            wants_identifier_inventory=(
                self.identifier_query_analyzer.looks_like_inventory_query(normalized)
            ),
        )

    @staticmethod
    def _detail_entity_type(normalized: str) -> StructuredEntityType | None:
        if not any(term in normalized for term in _DETAIL_TERMS):
            return None
        if any(term in normalized for term in _MANUFACTURER_TERMS):
            return StructuredEntityType.MANUFACTURER
        if any(term in normalized for term in _SUPPLIER_TERMS):
            return StructuredEntityType.SUPPLIER
        if any(term in normalized for term in _SPARE_PART_TERMS):
            return StructuredEntityType.SPARE_PART
        if any(term in normalized for term in _EQUIPMENT_TERMS):
            return StructuredEntityType.EQUIPMENT
        if "maintenance task" in normalized:
            return StructuredEntityType.MAINTENANCE_TASK
        if any(term in normalized for term in _WEBSITE_TERMS + _COUNTRY_TERMS):
            return StructuredEntityType.MANUFACTURER
        return None

    @staticmethod
    def _ordered_unique(
        values: list[StructuredEntityType],
    ) -> list[StructuredEntityType]:
        ordered: list[StructuredEntityType] = []
        for value in values:
            if value not in ordered:
                ordered.append(value)
        return ordered
