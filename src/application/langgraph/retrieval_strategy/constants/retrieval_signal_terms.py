from __future__ import annotations

from src.domain.common import ChunkType

IDENTIFIER_TERMS = (
    "part no",
    "part number",
    "serial number",
    "model",
    "order code",
    "tag",
    "certificate number",
    "drawing number",
    "manufacturer",
    "supplier",
    "made by",
    "manufactured by",
    "id ",
)
SPECIFICATION_TERMS = (
    "specification",
    "specifications",
    "specs",
    "technical specification",
    "technical specifications",
    "technical data",
    "pressure",
    "test pressure",
    "design pressure",
    "temperature",
    "voltage",
    "power",
    "capacity",
    "rating",
    "weight",
    "dimension",
    "material",
    "dn",
    "bar",
    "kw",
    "volt",
    "volts",
    "amp",
    "amps",
    "ampere",
    "amperes",
    "mm",
)
# NOTE on cross-module duplication (investigated, not merged): see the
# matching note above RetrievalQueryIntentInferer._MAINTENANCE_MARKERS in
# src/application/workflows/retrieval/retrieval_query_intent_inferer.py. This
# list also conflates general-maintenance-topic terms ("maintenance",
# "service", "inspection") with interval/frequency-specific terms ("daily",
# "weekly", "monthly", "quarterly", "annually", "schedule") in one bucket --
# a separate internal design difference from this module's own float-weighted
# signal scoring, not something fixed as part of the maintenance-signal
# cross-module investigation. Left separate from the other two lists,
# deliberately, for the same reason: this feeds LangGraph strategy-signal
# weighting, a different downstream decision with a different
# false-positive tolerance than either retrieval targeting or answer
# formatting.
MAINTENANCE_TERMS = (
    "maintenance",
    "maintenance interval",
    "maintenance intervals",
    "service",
    "service interval",
    "service intervals",
    "inspection",
    "inspection interval",
    "inspection intervals",
    "interval",
    "operating hours",
    "lubrication",
    "oil change",
    "replace filter",
    "preventive maintenance",
    "schedule",
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "annually",
)
PROCEDURE_TERMS = (
    "how to",
    "procedure",
    "steps",
    "install",
    "remove",
    "replace",
    "start",
    "stop",
    "operate",
    "commission",
    "dismantle",
    "assemble",
    "configure",
)
TROUBLESHOOTING_TERMS = (
    "troubleshooting",
    "fault",
    "alarm",
    "error",
    "cause",
    "remedy",
    "problem",
    "troubleshoot",
    "failure",
    "symptom",
)
CERTIFICATION_TERMS = (
    "certificate",
    "certification",
    "inspection",
    "approval",
    "lr",
    "atex",
    "iecex",
    "surveyor",
    "issued",
    "compliance",
    "valid",
)
DRAWING_TERMS = (
    "drawing",
    "diagram",
    "schematic",
    "layout",
    "dimensions",
    "view",
)
FIGURE_TERMS = ("figure", "fig.", "image", "picture")
TABLE_TERMS = ("table", "list", "schedule", "matrix", "row", "column", "values", "data table")
SECTION_TERMS = ("section", "page", "heading", "chapter", "appendix", "path")

CHUNK_TYPE_TO_CATEGORY: dict[ChunkType, str] = {
    ChunkType.TECHNICAL_SPECIFICATION: "specification",
    ChunkType.SPARE_PARTS_TABLE: "table",
    ChunkType.CERTIFICATION_INFO: "certification",
    ChunkType.MAINTENANCE_INTERVAL: "maintenance",
    ChunkType.MAINTENANCE_PROCEDURE: "maintenance",
    ChunkType.OPERATION_INSTRUCTION: "procedure",
    ChunkType.INSTALLATION_INSTRUCTION: "procedure",
    ChunkType.TROUBLESHOOTING: "troubleshooting",
    ChunkType.DRAWING_REFERENCE: "drawing",
    ChunkType.OVERVIEW: "document_exploration",
}

ANSWER_INTENT_TO_CATEGORY: dict[str, str] = {
    "maintenance_summary": "maintenance",
    "procedure_steps": "procedure",
    "specification_summary": "specification",
    "troubleshooting": "troubleshooting",
    "certification_summary": "certification",
    "identifier_lookup": "identifier",
    "table_summary": "table",
    "document_summary": "document_exploration",
}
