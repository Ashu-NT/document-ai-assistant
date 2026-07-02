import re

from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery

# Patterns that signal the user is asking about what a document contains or how
# it is structured, rather than asking for a specific fact inside the document.
#
# Each pattern covers a semantic shape rather than a literal phrase so that
# novel phrasings still match without a growing hardcoded list.
_EXPLORATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    # "what (information|content|data) is/are in/inside/within this/the ..."
    re.compile(
        r"what\s+(information|content|data|details?)\s+(is|are)\s+(in|inside|within|available\s+in)\b"
    ),
    # "what does this/the document/manual/pdf/file contain/cover/include/have"
    re.compile(
        r"what\s+does\s+(this|the)\s+\S+\s+(contain|cover|include|have|describe|document)\b"
    ),
    # "what sections/chapters/topics/identifiers/tables/figures/... are/exist/available/covered"
    re.compile(
        r"what\s+(sections?|chapters?|topics?|subjects?|parts?|identifiers?|part\s+numbers?|"
        r"serial\s+numbers?|model\s+numbers?|tables?|figures?|images?|pictures?|assets?|"
        r"equipment|components?|products?|devices?|systems?)\s+"
        r"(are|is|exist|available|present|covered|listed|documented|mentioned|referenced|in\s+(this|the))\b"
    ),
    # "what is documented/available/covered/described here or in this"
    re.compile(
        r"what\s+is\s+(documented|available|covered|described|listed|included)\s+"
        r"(here|in\s+this|in\s+the)\b"
    ),
    # "what is in this document/pdf/manual/file/report"
    re.compile(
        r"what\s+is\s+in\s+(this|the)\s+(document|pdf|manual|file|report|guide|datasheet|drawing)\b"
    ),
    # "what can I find in this"
    re.compile(r"what\s+(can|could)\s+\w+\s+find\s+(in|inside|within)\b"),
    # "list / show / enumerate / display sections / structure / identifiers / tables / ..."
    re.compile(
        r"(list|show|display|enumerate|give\s+me|provide)\s+(all\s+|the\s+)?"
        r"(sections?|chapters?|topics?|structure|contents?|identifiers?|tables?|figures?|assets?|equipment)\b"
    ),
    # "document / manual / pdf structure / outline / overview / contents / index"
    re.compile(
        r"(document|manual|pdf|file|report)\s+"
        r"(structure|outline|overview|contents?|index|inventory|coverage)\b"
    ),
    # "what topics/subjects/areas are covered/discussed/addressed in"
    re.compile(
        r"what\s+(topics?|subjects?|areas?|items?|things?)\s+(are|is)\s+"
        r"(covered|discussed|addressed|documented|included)\b"
    ),
    # "what is this document/manual/pdf about"
    re.compile(
        r"what\s+is\s+(this|the)\s+(document|manual|pdf|file|report|guide|datasheet)\s+about\b"
    ),
)
_EXPLICIT_IDENTIFIER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(serial|part|order|model|drawing|certificate|approval|position|tag)\s+"
        r"(number|numbers|no|code|codes|designation)\b"
    ),
    re.compile(r"\bspare\s+part\s+(number|no|code)\b"),
    re.compile(r"\bordering\s+code\b"),
    re.compile(r"\border\s+code\b"),
    re.compile(r"\bwhat\s+product\s+is\s+type\s+[a-z0-9-]+\b"),
    re.compile(r"\bwhat\s+is\s+type\s+[a-z0-9-]+\b"),
    re.compile(r"\bwhat\s+is\s+position\s+[a-z0-9-]+\b"),
)
_IDENTIFIER_LISTING_VERBS: tuple[str, ...] = (
    "list",
    "show",
    "display",
    "enumerate",
    "provide",
    "give me",
    "find all",
)
_IDENTIFIER_LISTING_MARKERS: tuple[str, ...] = (
    "serial",
    "part",
    "order code",
    "order number",
    "model",
    "drawing",
    "certificate",
    "tag",
    "manufacturer",
    "supplier",
)
_OVERVIEW_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bwhat\s+does\s+.+\s+do\b"),
    re.compile(r"\bwhat\s+is\s+.+\s+used\s+for\b"),
    re.compile(r"\bwhat\s+is\s+the\s+(purpose|function)\s+of\b"),
    re.compile(r"\bhow\s+does\s+.+\s+work\b"),
)
_EXPLICIT_PROCEDURE_MARKERS: tuple[str, ...] = (
    "how to",
    "procedure",
    "steps",
    "step",
    "install",
    "configure",
    "calibrate",
    "start",
    "run",
    "restart",
    "remove",
    "connect",
    "shutdown",
    "commission",
    "commissioning",
)
_MAINTENANCE_MARKERS: tuple[str, ...] = (
    "maintenance",
    "service interval",
    "service schedule",
    "inspection schedule",
    "maintenance interval",
    "maintenance intervals",
    "maintenance task",
    "maintenance tasks",
    "preventive maintenance",
    "oil change",
    "lubricat",
    "grease",
    "how often",
    "interval",
)


def _is_document_exploration(query_text: str) -> bool:
    for pattern in _EXPLORATION_PATTERNS:
        if pattern.search(query_text):
            return True
    return False


def _is_explicit_identifier_lookup(
    query_text: str,
    query: RetrievalQuery | None,
) -> bool:
    if any(pattern.search(query_text) for pattern in _EXPLICIT_IDENTIFIER_PATTERNS):
        return True

    if query is None or not query.has_identifiers():
        return False

    if any(
        marker in query_text
        for marker in (
            " mean",
            " means",
            "meaning",
            "stand for",
            "stands for",
            "designation",
            "position ",
            "type ",
        )
    ):
        return True

    return bool(
        re.search(r"\bwhat\s+does\s+[a-z0-9-]+\s+mean\b", query_text)
        or re.search(r"\bwhat\s+is\s+position\s+[a-z0-9-]+\b", query_text)
    )


def _is_overview_query(query_text: str) -> bool:
    if any(pattern.search(query_text) for pattern in _OVERVIEW_PATTERNS):
        return True

    return any(
        marker in query_text
        for marker in (
            "overview",
            "summary",
            "introduction",
            "explain",
            "objective",
            "purpose",
            "function",
        )
    )


def _contains_identifier_reference(query_text: str) -> bool:
    return any(marker in query_text for marker in _IDENTIFIER_LISTING_MARKERS)


def _looks_like_identifier_listing_query(query_text: str) -> bool:
    if not any(marker in query_text for marker in _IDENTIFIER_LISTING_VERBS):
        return False
    return _contains_identifier_reference(query_text)


def _is_maintenance_query(query_text: str) -> bool:
    return any(marker in query_text for marker in _MAINTENANCE_MARKERS)


def _is_explicit_procedure_query(query_text: str) -> bool:
    return any(marker in query_text for marker in _EXPLICIT_PROCEDURE_MARKERS)


def _infer_from_chunk_types(query: RetrievalQuery) -> RetrievalQueryIntent | None:
    if ChunkType.SPARE_PARTS_TABLE in query.chunk_types:
        return RetrievalQueryIntent.TABLE
    if ChunkType.DRAWING_REFERENCE in query.chunk_types:
        return RetrievalQueryIntent.FIGURE
    if ChunkType.SAFETY_WARNING in query.chunk_types:
        return RetrievalQueryIntent.SAFETY
    if ChunkType.TROUBLESHOOTING in query.chunk_types:
        return RetrievalQueryIntent.TROUBLESHOOTING
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.MAINTENANCE_INTERVAL,
            ChunkType.MAINTENANCE_PROCEDURE,
        }
    ):
        return RetrievalQueryIntent.MAINTENANCE
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.INSTALLATION_INSTRUCTION,
            ChunkType.OPERATION_INSTRUCTION,
        }
    ):
        return RetrievalQueryIntent.PROCEDURE
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.TECHNICAL_SPECIFICATION,
            ChunkType.CERTIFICATION_INFO,
        }
    ):
        return RetrievalQueryIntent.SPECIFICATION
    return None


class RetrievalQueryIntentInferer:
    def infer(self, query: RetrievalQuery | None) -> RetrievalQueryIntent:
        if query is None:
            return RetrievalQueryIntent.GENERAL

        query_text = query.effective_query().strip().lower()
        if query_text and _is_document_exploration(query_text):
            return RetrievalQueryIntent.DOCUMENT_EXPLORATION

        if not query_text:
            return _infer_from_chunk_types(query) or RetrievalQueryIntent.GENERAL

        if any(
            marker in query_text
            for marker in ("figure", "diagram", "drawing", "schematic", "image")
        ):
            return RetrievalQueryIntent.FIGURE
        if any(
            marker in query_text
            for marker in ("table", "spare part", "parts list", "spare parts list", "matrix")
        ):
            return RetrievalQueryIntent.TABLE
        if _is_explicit_identifier_lookup(query_text, query):
            return RetrievalQueryIntent.IDENTIFIER
        if _looks_like_identifier_listing_query(query_text):
            return RetrievalQueryIntent.IDENTIFIER
        if any(
            marker in query_text
            for marker in (
                "serial number",
                "part number",
                "part no",
                "order code",
                "order number",
                "model number",
                "drawing number",
                "certificate number",
                "what is position ",
            )
        ):
            return RetrievalQueryIntent.IDENTIFIER
        if any(
            marker in query_text
            for marker in (
                "specification",
                "specifications",
                "parameter",
                "voltage",
                "current",
                "tolerance",
                "dimension",
                "torque",
                "pressure",
                "approval",
                "certificate",
            )
        ):
            return RetrievalQueryIntent.SPECIFICATION
        if any(
            marker in query_text
            for marker in (
                "troubleshoot",
                "problem",
                "fault",
                "error",
                "not working",
                "causes",
                "remedies",
                "diagnose",
                "symptom",
            )
        ):
            return RetrievalQueryIntent.TROUBLESHOOTING
        if any(
            marker in query_text
            for marker in ("safety", "warning", "danger", "hazard")
        ):
            return RetrievalQueryIntent.SAFETY
        if _is_maintenance_query(query_text) and not _is_explicit_procedure_query(
            query_text
        ):
            return RetrievalQueryIntent.MAINTENANCE
        if any(
            marker in query_text
            for marker in (
                "how to",
                "procedure",
                "steps",
                "step",
                "replace",
                "install",
                "configure",
                "calibrate",
                "start",
                "run",
                "restart",
                "remove",
                "connect",
                "shutdown",
                "commission",
                "commissioning",
                "lubricate",
            )
        ):
            return RetrievalQueryIntent.PROCEDURE
        if _is_overview_query(query_text):
            return RetrievalQueryIntent.OVERVIEW
        chunk_type_intent = _infer_from_chunk_types(query)
        if chunk_type_intent is not None:
            return chunk_type_intent
        if query.has_identifiers():
            return RetrievalQueryIntent.IDENTIFIER

        return RetrievalQueryIntent.GENERAL
