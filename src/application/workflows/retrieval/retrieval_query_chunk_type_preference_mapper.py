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
            preferences = [
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.CERTIFICATION_INFO,
                ChunkType.MAINTENANCE_INTERVAL,
                ChunkType.OPERATION_INSTRUCTION,
                ChunkType.INSTALLATION_INSTRUCTION,
                ChunkType.MAINTENANCE_PROCEDURE,
                ChunkType.GENERAL,
                ChunkType.SPARE_PARTS_TABLE,
            ]
            if any(
                marker in query_text
                for marker in ("certificate", "approval", "iecex", "atex")
            ):
                preferences.insert(0, ChunkType.CERTIFICATION_INFO)
            if any(
                marker in query_text
                for marker in ("pressure", "torque", "flow", "set", "setting", "adjust", "optimis", "optimiz")
            ):
                preferences.insert(1, ChunkType.OPERATION_INSTRUCTION)
            return self._unique(preferences)

        if intent == RetrievalQueryIntent.MAINTENANCE:
            preferences = [
                ChunkType.MAINTENANCE_INTERVAL,
                ChunkType.MAINTENANCE_PROCEDURE,
                ChunkType.SPARE_PARTS_TABLE,
                ChunkType.OPERATION_INSTRUCTION,
                ChunkType.SAFETY_WARNING,
                ChunkType.GENERAL,
                ChunkType.OVERVIEW,
            ]
            if any(
                marker in query_text
                for marker in ("interval", "schedule", "how often", "hours", "daily", "weekly")
            ):
                preferences = [
                    ChunkType.MAINTENANCE_INTERVAL,
                    ChunkType.SPARE_PARTS_TABLE,
                    ChunkType.MAINTENANCE_PROCEDURE,
                    ChunkType.OPERATION_INSTRUCTION,
                    ChunkType.GENERAL,
                    ChunkType.OVERVIEW,
                ]
            return self._unique(preferences)

        if intent == RetrievalQueryIntent.PROCEDURE:
            preferences = [
                ChunkType.OPERATION_INSTRUCTION,
                ChunkType.MAINTENANCE_PROCEDURE,
                ChunkType.INSTALLATION_INSTRUCTION,
                ChunkType.MAINTENANCE_INTERVAL,
                ChunkType.TROUBLESHOOTING,
                ChunkType.TECHNICAL_SPECIFICATION,
                ChunkType.SAFETY_WARNING,
                ChunkType.GENERAL,
                ChunkType.OVERVIEW,
            ]
            if any(
                marker in query_text
                for marker in ("how often", "task", "interval", "schedule", "lubricat", "hours")
            ):
                preferences = [
                    ChunkType.MAINTENANCE_INTERVAL,
                    ChunkType.MAINTENANCE_PROCEDURE,
                    ChunkType.OPERATION_INSTRUCTION,
                    ChunkType.SPARE_PARTS_TABLE,
                    ChunkType.INSTALLATION_INSTRUCTION,
                    ChunkType.TROUBLESHOOTING,
                    ChunkType.GENERAL,
                    ChunkType.OVERVIEW,
                ]
            elif any(
                marker in query_text
                for marker in (
                    "commission",
                    "installation",
                    "electrical connection",
                    "connect",
                    "objective",
                )
            ):
                preferences = [
                    ChunkType.INSTALLATION_INSTRUCTION,
                    ChunkType.OPERATION_INSTRUCTION,
                    ChunkType.MAINTENANCE_PROCEDURE,
                    ChunkType.TECHNICAL_SPECIFICATION,
                    ChunkType.GENERAL,
                    ChunkType.OVERVIEW,
                ]
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
            return self._unique(
                [
                    ChunkType.OVERVIEW,
                    ChunkType.GENERAL,
                    ChunkType.OPERATION_INSTRUCTION,
                    ChunkType.INSTALLATION_INSTRUCTION,
                    ChunkType.TECHNICAL_SPECIFICATION,
                ]
            )

        # QuestionAnsweringWorkflow should normally route DOCUMENT_EXPLORATION away from
        # RetrievalWorkflow before a query reaches this mapper. This branch is a safety
        # net for callers that use RetrievalWorkflow directly with an exploration question.
        if intent == RetrievalQueryIntent.DOCUMENT_EXPLORATION:
            return [ChunkType.OVERVIEW, ChunkType.GENERAL]

        return list(query.chunk_types)

    @staticmethod
    def _unique(values: list[ChunkType]) -> list[ChunkType]:
        ordered: list[ChunkType] = []
        for value in values:
            if value not in ordered:
                ordered.append(value)
        return ordered
