from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery


class RetrievalQueryIntentInferer:
    def infer(self, query: RetrievalQuery | None) -> RetrievalQueryIntent:
        if query is None:
            return RetrievalQueryIntent.GENERAL

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

        query_text = query.effective_query().strip().lower()
        if not query_text:
            return RetrievalQueryIntent.GENERAL

        if any(
            marker in query_text
            for marker in ("figure", "diagram", "drawing", "schematic", "image")
        ):
            return RetrievalQueryIntent.FIGURE
        if any(
            marker in query_text
            for marker in ("table", "part number", "part no", "spare part", "list")
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
            )
        ):
            return RetrievalQueryIntent.PROCEDURE
        if any(
            marker in query_text
            for marker in ("overview", "summary", "introduction", "explain")
        ):
            return RetrievalQueryIntent.OVERVIEW

        return RetrievalQueryIntent.GENERAL
