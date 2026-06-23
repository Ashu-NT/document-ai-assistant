from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery


class RetrievalQueryChunkTypePreferenceMapper:
    def map(
        self,
        *,
        query: RetrievalQuery,
        intent: RetrievalQueryIntent,
    ) -> list[ChunkType]:
        query_text = query.effective_query().lower()

        if intent == RetrievalQueryIntent.IDENTIFIER:
            preferences = [
                ChunkType.SPARE_PARTS_TABLE,
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.CERTIFICATION_INFO,
                ChunkType.DRAWING_REFERENCE,
                ChunkType.GENERAL,
            ]
            if any(
                marker in query_text
                for marker in ("certificate", "approval", "iecex", "atex")
            ):
                preferences.insert(0, ChunkType.CERTIFICATION_INFO)
            return self._unique(preferences)

        if intent == RetrievalQueryIntent.TABLE:
            return self._unique(
                [
                    ChunkType.SPARE_PARTS_TABLE,
                    ChunkType.TECHNICAL_SPECIFICATION,
                    ChunkType.CERTIFICATION_INFO,
                    ChunkType.GENERAL,
                ]
            )

        if intent == RetrievalQueryIntent.SPECIFICATION:
            return self._unique(
                [
                    ChunkType.TECHNICAL_SPECIFICATION,
                    ChunkType.CERTIFICATION_INFO,
                    ChunkType.SPARE_PARTS_TABLE,
                    ChunkType.INSTALLATION_INSTRUCTION,
                    ChunkType.MAINTENANCE_PROCEDURE,
                    ChunkType.GENERAL,
                ]
            )

        if intent == RetrievalQueryIntent.PROCEDURE:
            preferences = [
                ChunkType.OPERATION_INSTRUCTION,
                ChunkType.MAINTENANCE_PROCEDURE,
                ChunkType.TROUBLESHOOTING,
                ChunkType.SAFETY_WARNING,
                ChunkType.GENERAL,
            ]
            if any(
                marker in query_text
                for marker in ("how often", "interval", "schedule", "lubricat", "hours")
            ):
                preferences.insert(0, ChunkType.MAINTENANCE_INTERVAL)
            return self._unique(preferences)

        if intent == RetrievalQueryIntent.TROUBLESHOOTING:
            return self._unique(
                [
                    ChunkType.TROUBLESHOOTING,
                    ChunkType.OPERATION_INSTRUCTION,
                    ChunkType.MAINTENANCE_PROCEDURE,
                    ChunkType.GENERAL,
                ]
            )

        if intent == RetrievalQueryIntent.SAFETY:
            return self._unique(
                [
                    ChunkType.SAFETY_WARNING,
                    ChunkType.OPERATION_INSTRUCTION,
                    ChunkType.TROUBLESHOOTING,
                    ChunkType.GENERAL,
                ]
            )

        if intent == RetrievalQueryIntent.FIGURE:
            return self._unique(
                [
                    ChunkType.DRAWING_REFERENCE,
                    ChunkType.TECHNICAL_SPECIFICATION,
                    ChunkType.GENERAL,
                ]
            )

        if intent == RetrievalQueryIntent.OVERVIEW:
            return [ChunkType.OVERVIEW, ChunkType.GENERAL]

        return list(query.chunk_types)

    @staticmethod
    def _unique(values: list[ChunkType]) -> list[ChunkType]:
        ordered: list[ChunkType] = []
        for value in values:
            if value not in ordered:
                ordered.append(value)
        return ordered
