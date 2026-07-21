from src.application.workflows.retrieval.intent.retrieval_query_focus_predicates import (
    requests_certification_evidence,
    requests_installation_or_commissioning_instructions,
    requests_maintenance_interval_evidence,
    requests_specification_setting_instructions,
)
from src.application.workflows.retrieval.query_analysis.retrieval_query_identifier_extractor import (
    RetrievalQueryIdentifierExtractor,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery

# Maps extract_typed()'s identifier-format labels to the chunk type most
# likely to hold that specific format's evidence -- narrower and more
# reliable than the IDENTIFIER intent's generic preference order below when
# the query names a specific identifier format (e.g. "drawing no. 4471").
_IDENTIFIER_TYPE_CHUNK_TYPE_PREFERENCE: dict[str, ChunkType] = {
    "part_number": ChunkType.SPARE_PARTS_TABLE,
    "order_code": ChunkType.SPARE_PARTS_TABLE,
    "serial_number": ChunkType.TECHNICAL_SPECIFICATION,
    "model_number": ChunkType.TECHNICAL_SPECIFICATION,
    "tag_number": ChunkType.TECHNICAL_SPECIFICATION,
    "drawing_number": ChunkType.DRAWING_REFERENCE,
    "certificate_number": ChunkType.CERTIFICATION_INFO,
}


class RetrievalQueryChunkTypePreferenceMapper:
    def __init__(
        self,
        *,
        identifier_extractor: RetrievalQueryIdentifierExtractor | None = None,
    ) -> None:
        self._identifier_extractor = (
            identifier_extractor or RetrievalQueryIdentifierExtractor()
        )

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
            for match in self._identifier_extractor.extract_typed(query_text):
                preferred_type = _IDENTIFIER_TYPE_CHUNK_TYPE_PREFERENCE.get(
                    match.identifier_type
                )
                if preferred_type is not None:
                    preferences.insert(0, preferred_type)
            if requests_certification_evidence(query_text):
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
            if requests_certification_evidence(query_text):
                preferences.insert(0, ChunkType.CERTIFICATION_INFO)
            if requests_specification_setting_instructions(query_text):
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
            if requests_maintenance_interval_evidence(query_text) or "hours" in query_text:
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
            if (
                requests_maintenance_interval_evidence(query_text)
                or "task" in query_text
                or "lubricat" in query_text
                or "hours" in query_text
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
            elif requests_installation_or_commissioning_instructions(query_text):
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
