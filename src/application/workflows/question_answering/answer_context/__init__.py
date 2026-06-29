from src.application.workflows.question_answering.answer_context.structured_answer_context import (
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
    "AnswerContextOrganizer",
    "AnswerSectionGroup",
    "AnswerSource",
    "AnswerSourceGroup",
    "MaintenanceEntryMerger",
    "StructuredAnswerContext",
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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
