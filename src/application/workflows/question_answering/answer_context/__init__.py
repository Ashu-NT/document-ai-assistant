from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
    AnswerSectionGroup,
    AnswerSource,
    AnswerSourceGroup,
    StructuredAnswerContext,
)

__all__ = [
    "AnswerContextOrganizer",
    "AnswerKeyValue",
    "AnswerMaintenanceEntry",
    "AnswerMaintenanceReference",
    "AnswerSectionGroup",
    "AnswerSource",
    "AnswerSourceGroup",
    "MaintenanceEntryMerger",
    "StructuredAnswerContext",
    "StructuredFactKeyValueBuilder",
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
    if name == "StructuredFactKeyValueBuilder":
        from src.application.workflows.question_answering.answer_context.structured_fact_key_value_builder import (
            StructuredFactKeyValueBuilder,
        )

        return StructuredFactKeyValueBuilder
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
