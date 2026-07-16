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
# vs. ExtractionPromptType enum members here), so a shared vocabulary would
# need a lossy translation layer between enums that don't correspond 1:1
# rather than removing real duplication. Precedent from that pass: only
# consolidate when two lists drift on the SAME narrow concept (e.g. the
# identifier-inventory regex/marker duplication fixed alongside this note,
# see identifier_value_pattern.py) -- not force unrelated taxonomies
# together because they're superficially similar in shape.
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.workflows.shared.maintenance_signal_detection import (
    mentions_maintenance_interval,
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
        entity_types: list[ExtractionPromptType] = []

        if detail_entity_type is not None:
            entity_types.append(detail_entity_type)
            if (
                detail_entity_type in {
                    ExtractionPromptType.MANUFACTURER,
                    ExtractionPromptType.SUPPLIER,
                }
                and any(term in normalized for term in _CONTACT_DETAIL_TERMS)
            ):
                entity_types.append(ExtractionPromptType.CONTACT_POINT)

        if any(term in normalized for term in _MANUFACTURER_TERMS):
            entity_types.append(ExtractionPromptType.MANUFACTURER)
        if any(term in normalized for term in _SUPPLIER_TERMS):
            entity_types.append(ExtractionPromptType.SUPPLIER)
        if any(term in normalized for term in _SPARE_PART_TERMS):
            entity_types.append(ExtractionPromptType.SPARE_PART)
        if any(term in normalized for term in _EQUIPMENT_TERMS):
            entity_types.append(ExtractionPromptType.EQUIPMENT)
        if any(term in normalized for term in _SPECIFICATION_TERMS):
            entity_types.extend(
                [
                    ExtractionPromptType.SPECIFICATION,
                    ExtractionPromptType.EQUIPMENT,
                ]
            )
        if mentions_maintenance_interval(normalized):
            entity_types.extend(
                [
                    ExtractionPromptType.MAINTENANCE_INTERVAL,
                    ExtractionPromptType.MAINTENANCE_TASK,
                ]
            )
        elif any(term in normalized for term in _MAINTENANCE_TERMS):
            entity_types.extend(
                [
                    ExtractionPromptType.MAINTENANCE_TASK,
                    ExtractionPromptType.PROCEDURE,
                ]
            )
        if any(term in normalized for term in _PROCEDURE_TERMS):
            entity_types.append(ExtractionPromptType.PROCEDURE)
        if any(term in normalized for term in _TROUBLESHOOTING_TERMS):
            entity_types.append(ExtractionPromptType.TROUBLESHOOTING)
        if any(term in normalized for term in _SAFETY_TERMS):
            entity_types.append(ExtractionPromptType.SAFETY_WARNING)

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
                    ExtractionPromptType.MAINTENANCE_TASK,
                    ExtractionPromptType.MAINTENANCE_INTERVAL,
                    ExtractionPromptType.PROCEDURE,
                ]
            )
        elif intent == RetrievalQueryIntent.PROCEDURE.value:
            entity_types.append(ExtractionPromptType.PROCEDURE)
        elif intent == RetrievalQueryIntent.TROUBLESHOOTING.value:
            entity_types.append(ExtractionPromptType.TROUBLESHOOTING)
        elif intent == RetrievalQueryIntent.SPECIFICATION.value:
            entity_types.extend(
                [
                    ExtractionPromptType.SPECIFICATION,
                    ExtractionPromptType.EQUIPMENT,
                ]
            )

        if detected_identifiers:
            entity_types.extend(
                [
                    ExtractionPromptType.SPARE_PART,
                    ExtractionPromptType.EQUIPMENT,
                    ExtractionPromptType.SPECIFICATION,
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
    def _detail_entity_type(normalized: str) -> ExtractionPromptType | None:
        if not any(term in normalized for term in _DETAIL_TERMS):
            return None
        if any(term in normalized for term in _MANUFACTURER_TERMS):
            return ExtractionPromptType.MANUFACTURER
        if any(term in normalized for term in _SUPPLIER_TERMS):
            return ExtractionPromptType.SUPPLIER
        if any(term in normalized for term in _SPARE_PART_TERMS):
            return ExtractionPromptType.SPARE_PART
        if any(term in normalized for term in _EQUIPMENT_TERMS):
            return ExtractionPromptType.EQUIPMENT
        if "maintenance task" in normalized:
            return ExtractionPromptType.MAINTENANCE_TASK
        if any(term in normalized for term in _WEBSITE_TERMS + _COUNTRY_TERMS):
            return ExtractionPromptType.MANUFACTURER
        return None

    @staticmethod
    def _ordered_unique(
        values: list[ExtractionPromptType],
    ) -> list[ExtractionPromptType]:
        ordered: list[ExtractionPromptType] = []
        for value in values:
            if value not in ordered:
                ordered.append(value)
        return ordered
