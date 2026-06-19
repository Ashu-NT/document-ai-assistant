from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.parsing_workflow_result import (
    ParsingWorkflowResult,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument

__all__ = [
    "CanonicalElement",
    "ParsingWorkflow",
    "ParsingWorkflowResult",
    "RawParsedDocument",
]


def __getattr__(name: str):
    if name == "ParsingWorkflow":
        from src.application.workflows.parsing.parsing_workflow import ParsingWorkflow

        return ParsingWorkflow

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
