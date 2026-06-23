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


def _is_document_exploration(query_text: str) -> bool:
    for pattern in _EXPLORATION_PATTERNS:
        if pattern.search(query_text):
            return True
    return False


class RetrievalQueryIntentInferer:
    def infer(self, query: RetrievalQuery | None) -> RetrievalQueryIntent:
        if query is None:
            return RetrievalQueryIntent.GENERAL

        query_text = query.effective_query().strip().lower()
        if query_text and _is_document_exploration(query_text):
            return RetrievalQueryIntent.DOCUMENT_EXPLORATION

        if ChunkType.SPARE_PARTS_TABLE in query.chunk_types:
            return RetrievalQueryIntent.TABLE
        if ChunkType.DRAWING_REFERENCE in query.chunk_types:
            return RetrievalQueryIntent.FIGURE
        if ChunkType.TECHNICAL_SPECIFICATION in query.chunk_types:
            return RetrievalQueryIntent.SPECIFICATION
        if ChunkType.CERTIFICATION_INFO in query.chunk_types:
            return RetrievalQueryIntent.SPECIFICATION
        if ChunkType.SAFETY_WARNING in query.chunk_types:
            return RetrievalQueryIntent.SAFETY
        if ChunkType.TROUBLESHOOTING in query.chunk_types:
            return RetrievalQueryIntent.TROUBLESHOOTING
        if query.has_identifiers():
            return RetrievalQueryIntent.IDENTIFIER
        if any(
            chunk_type in query.chunk_types
            for chunk_type in {
                ChunkType.MAINTENANCE_PROCEDURE,
                ChunkType.MAINTENANCE_INTERVAL,
                ChunkType.INSTALLATION_INSTRUCTION,
                ChunkType.OPERATION_INSTRUCTION,
            }
        ):
            return RetrievalQueryIntent.PROCEDURE

        if not query_text:
            return RetrievalQueryIntent.GENERAL

        if any(
            marker in query_text
            for marker in ("figure", "diagram", "drawing", "schematic", "image")
        ):
            return RetrievalQueryIntent.FIGURE
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
                "what does ",
                "what is position ",
            )
        ):
            return RetrievalQueryIntent.IDENTIFIER
        if any(
            marker in query_text
            for marker in ("table", "spare part", "parts list", "matrix", "list")
        ):
            return RetrievalQueryIntent.TABLE
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
            for marker in ("troubleshoot", "problem", "fault", "error", "not working")
        ):
            return RetrievalQueryIntent.TROUBLESHOOTING
        if any(
            marker in query_text
            for marker in ("safety", "warning", "danger", "hazard")
        ):
            return RetrievalQueryIntent.SAFETY
        if any(
            marker in query_text
            for marker in (
                "how to",
                "procedure",
                "steps",
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
                "lubricate",
                "maintenance",
                "how often",
                "interval",
            )
        ):
            return RetrievalQueryIntent.PROCEDURE
        if any(
            marker in query_text
            for marker in ("overview", "summary", "introduction", "explain")
        ):
            return RetrievalQueryIntent.OVERVIEW

        return RetrievalQueryIntent.GENERAL
