from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
    AnswerRelationship,
    AnswerSectionGroup,
    AnswerSource,
    AnswerSourceGroup,
    AnswerStructuredEntity,
    StructuredAnswerContext,
)
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTable,
    AnswerTableRow,
)

__all__ = [
    "AnswerContextOrganizer",
    "AnswerKeyValue",
    "AnswerMaintenanceEntry",
    "AnswerMaintenanceReference",
    "AnswerRelationship",
    "AnswerSectionGroup",
    "AnswerSource",
    "AnswerSourceGroup",
    "AnswerStructuredEntity",
    "AnswerTable",
    "AnswerTableRow",
    "MaintenanceEntryMerger",
    "StructuredAnswerContext",
    "StructuredEvidenceViewBuilder",
    "StructuredFactKeyValueBuilder",
    "StructuredSourceBuilder",
]


def __getattr__(name: str):
    if name == "AnswerContextOrganizer":
        from src.application.workflows.question_answering.answer_context.answer_context_organizer import (
            AnswerContextOrganizer,
        )

        return AnswerContextOrganizer
    if name == "MaintenanceEntryMerger":
        from src.application.workflows.question_answering.answer_context.maintenance_entry_merger import (
            MaintenanceEntryMerger,
        )

        return MaintenanceEntryMerger
    if name == "StructuredEvidenceViewBuilder":
        from src.application.workflows.question_answering.answer_context.structured_evidence_view_builder import (
            StructuredEvidenceViewBuilder,
        )

        return StructuredEvidenceViewBuilder
    if name == "StructuredFactKeyValueBuilder":
        from src.application.workflows.question_answering.answer_context.structured_fact_key_value_builder import (
            StructuredFactKeyValueBuilder,
        )

        return StructuredFactKeyValueBuilder
    if name == "StructuredSourceBuilder":
        from src.application.workflows.question_answering.answer_context.structured_source_builder import (
            StructuredSourceBuilder,
        )

        return StructuredSourceBuilder
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
