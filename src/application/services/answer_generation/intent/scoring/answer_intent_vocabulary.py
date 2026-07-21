from __future__ import annotations

import re

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.domain.common import ChunkType

# Bumped whenever the scoring buckets, weights, or term lists below change
# materially -- mirrors RETRIEVAL_INTENT_RULES_VERSION's convention (and the
# `*_PROMPT_VERSION` pattern every LLM-prompt classifier already uses), so a
# future fallback-rate report for answer-intent can correlate a shift against
# a specific rule-pack version rather than an untracked code change.
ANSWER_INTENT_RULES_VERSION = "v1"

SPECIFICATION_TERMS = (
    "specification",
    "specifications",
    "spec",
    "technical data",
    "technical details",
    "pressure",
    "temperature",
    "size",
    "dimension",
    "rating",
    "capacity",
    "voltage",
    "current",
    "material",
    "power",
    "dn ",
)
# NOTE on cross-module duplication (investigated, not merged): see the
# matching note above RetrievalQueryIntentInferer._MAINTENANCE_MARKERS in
# src/application/workflows/retrieval/retrieval_query_intent_inferer.py.
# This list is intentionally broader (bare "service"/"inspection",
# "overhaul", "routine maintenance") than the retrieval inferer's -- answer
# FORMATTING tolerates more false positives than retrieval TARGETING does,
# since misjudging the answer's shape is a lower-cost mistake than fetching
# the wrong chunk types. A third, also-drifted list exists in
# RetrievalSignalExtractor._MAINTENANCE_TERMS for LangGraph strategy
# signals. Not unified -- three different downstream decisions with
# different false-positive tolerances.
MAINTENANCE_TERMS = (
    "maintenance",
    "maintenance task",
    "maintenance tasks",
    "maintenance schedule",
    "maintenance interval",
    "maintenance intervals",
    "preventive maintenance",
    "service interval",
    "service schedule",
    "inspection schedule",
    "routine maintenance",
    "maintenance checklist",
    "interval",
    "service",
    "inspection",
    "oil change",
    "lubricate",
    "lubrication",
    "grease",
    "overhaul",
)
PROCEDURE_TERMS = (
    "how to",
    "how do i",
    "how can i",
    "procedure",
    "steps",
    "step",
    "install",
    "disassemble",
    "assemble",
    "remove",
    "replace",
    "start",
    "stop",
    "operate",
    "shutdown",
    "commission",
    "commissioning",
    "connect",
    "configure",
)
SAFETY_TERMS = ("warning", "danger", "safety", "caution", "hazard")
TROUBLESHOOTING_TERMS = (
    "fault",
    "error",
    "alarm",
    "problem",
    "cause",
    "remedy",
    "troubleshoot",
    "symptom",
)
CERTIFICATION_TERMS = (
    "certificate",
    "approval",
    "surveyor",
    "compliance",
    "lr",
    "atex",
    "iecex",
)
# NOTE: bare "inspection" deliberately excluded (finding F5,
# outputs/architecture/answering_and_prompt_fresh_audit.md) -- it also
# appears in MAINTENANCE_TERMS, and that bucket already documents itself as
# intentionally broader/more false-positive-tolerant. A maintenance
# "inspection" is far more common in these documents than a certification
# one, so the ambiguous bare word belongs in the broader bucket; this one
# keeps only its unambiguous, certification-specific anchors.
IDENTIFIER_TERMS = (
    "part number",
    "serial number",
    "order code",
    "order number",
    "model number",
    "model",
    "tag",
    "drawing number",
    " id ",
)
TABLE_TERMS = ("table", "list", "schedule", "matrix")
DOCUMENT_SUMMARY_TERMS = (
    "summary",
    "summarize",
    "overview",
    "what is in",
    "what's in",
    "what does this document contain",
    "what does the document contain",
)
IDENTIFIER_LISTING_VERBS = (
    "list",
    "show",
    "display",
    "enumerate",
    "provide",
    "give me",
    "find all",
)
IDENTIFIER_LISTING_MARKERS = (
    "part number",
    "part no",
    "serial number",
    "serial no",
    "order code",
    "order number",
    "model number",
    "drawing number",
    "document number",
    "tag number",
    "equipment id",
    "certificate",
    "manufacturer",
    "supplier",
)
SPARE_PARTS_LIST_PHRASES = (
    "spare part list",
    "spare parts list",
    "spare part table",
    "spare parts table",
    "table of spare part",
    "table of spare parts",
    "spare part no list",
    "spare parts no list",
    "list of spare part",
    "list of spare parts",
)
MAINTENANCE_SUMMARY_PHRASES = (
    "maintenance task",
    "maintenance tasks",
    "maintenance schedule",
    "maintenance interval",
    "maintenance intervals",
    "preventive maintenance",
    "service interval",
    "service schedule",
    "inspection schedule",
    "routine maintenance",
    "maintenance checklist",
)
EXPLICIT_PROCEDURE_PHRASES = (
    "how to",
    "how do i",
    "how can i",
    "show steps",
    "show the steps",
    "what are the steps",
    "procedure for",
    "steps for",
)
TECHNICAL_VALUE_PATTERN = re.compile(
    r"\b("
    r"\d+(\.\d+)?\s*(bar|mm|cm|m|kw|w|v|a|hz|dn|pcs|pc)\b"
    r"|dn\s*\d+\b"
    r"|design pressure\b"
    r"|test pressure\b"
    r"|working pressure\b"
    r")",
    re.IGNORECASE,
)
STEP_PATTERN = re.compile(r"^\s*(\d+[\).\s]|[-*]\s+)", re.MULTILINE)
CHUNK_TYPE_TO_INTENT: dict[ChunkType, AnswerIntent] = {
    ChunkType.TECHNICAL_SPECIFICATION: AnswerIntent.SPECIFICATION_SUMMARY,
    ChunkType.CERTIFICATION_INFO: AnswerIntent.CERTIFICATION_SUMMARY,
    ChunkType.SPARE_PARTS_TABLE: AnswerIntent.TABLE_SUMMARY,
    ChunkType.MAINTENANCE_INTERVAL: AnswerIntent.MAINTENANCE_SUMMARY,
    ChunkType.MAINTENANCE_PROCEDURE: AnswerIntent.PROCEDURE_STEPS,
    ChunkType.OPERATION_INSTRUCTION: AnswerIntent.PROCEDURE_STEPS,
    ChunkType.INSTALLATION_INSTRUCTION: AnswerIntent.PROCEDURE_STEPS,
    ChunkType.SAFETY_WARNING: AnswerIntent.SAFETY_WARNINGS,
    ChunkType.TROUBLESHOOTING: AnswerIntent.TROUBLESHOOTING,
    ChunkType.OVERVIEW: AnswerIntent.DOCUMENT_SUMMARY,
}
RETRIEVAL_INTENT_TO_ANSWER_INTENT: dict[str, AnswerIntent] = {
    "maintenance": AnswerIntent.MAINTENANCE_SUMMARY,
    "specification": AnswerIntent.SPECIFICATION_SUMMARY,
    "procedure": AnswerIntent.PROCEDURE_STEPS,
    "troubleshooting": AnswerIntent.TROUBLESHOOTING,
    "safety": AnswerIntent.SAFETY_WARNINGS,
    "table": AnswerIntent.TABLE_SUMMARY,
    "identifier": AnswerIntent.IDENTIFIER_LOOKUP,
    "overview": AnswerIntent.DOCUMENT_SUMMARY,
    "document_exploration": AnswerIntent.DOCUMENT_SUMMARY,
}
INTENT_PRIORITY: tuple[AnswerIntent, ...] = (
    AnswerIntent.SPECIFICATION_SUMMARY,
    AnswerIntent.MAINTENANCE_SUMMARY,
    AnswerIntent.PROCEDURE_STEPS,
    AnswerIntent.SAFETY_WARNINGS,
    AnswerIntent.TROUBLESHOOTING,
    AnswerIntent.CERTIFICATION_SUMMARY,
    AnswerIntent.IDENTIFIER_LOOKUP,
    AnswerIntent.TABLE_SUMMARY,
    AnswerIntent.DOCUMENT_SUMMARY,
    AnswerIntent.GENERAL,
)
