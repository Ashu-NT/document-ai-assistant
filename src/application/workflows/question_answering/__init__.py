from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "AnswerContextOrganizer",
    "QuestionAnsweringRequest",
    "QuestionAnsweringResult",
    "QuestionAnsweringRoute",
    "QuestionAnsweringRouter",
    "QuestionAnsweringWorkflow",
    "StructuredAnswerContext",
]

if TYPE_CHECKING:
    from src.application.workflows.question_answering.answer_context import (
        AnswerContextOrganizer,
        StructuredAnswerContext,
    )
    from src.application.workflows.question_answering.question_answering_request import (
        QuestionAnsweringRequest,
    )
    from src.application.workflows.question_answering.question_answering_result import (
        QuestionAnsweringResult,
    )
    from src.application.workflows.question_answering.question_answering_route import (
        QuestionAnsweringRoute,
    )
    from src.application.workflows.question_answering.question_answering_router import (
        QuestionAnsweringRouter,
    )
    from src.application.workflows.question_answering.question_answering_workflow import (
        QuestionAnsweringWorkflow,
    )

_EXPORT_MAP = {
    "AnswerContextOrganizer": (
        "src.application.workflows.question_answering.answer_context",
        "AnswerContextOrganizer",
    ),
    "QuestionAnsweringRequest": (
        "src.application.workflows.question_answering.question_answering_request",
        "QuestionAnsweringRequest",
    ),
    "QuestionAnsweringResult": (
        "src.application.workflows.question_answering.question_answering_result",
        "QuestionAnsweringResult",
    ),
    "QuestionAnsweringRoute": (
        "src.application.workflows.question_answering.question_answering_route",
        "QuestionAnsweringRoute",
    ),
    "QuestionAnsweringRouter": (
        "src.application.workflows.question_answering.question_answering_router",
        "QuestionAnsweringRouter",
    ),
    "QuestionAnsweringWorkflow": (
        "src.application.workflows.question_answering.question_answering_workflow",
        "QuestionAnsweringWorkflow",
    ),
    "StructuredAnswerContext": (
        "src.application.workflows.question_answering.answer_context",
        "StructuredAnswerContext",
    ),
}


def __getattr__(name: str):
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = _EXPORT_MAP[name]
    module = import_module(module_name)
    return getattr(module, attr_name)
