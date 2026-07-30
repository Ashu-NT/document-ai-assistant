from typing import TYPE_CHECKING

from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument

__all__ = [
    "ParsedCanonicalElement",
    "ParsingWorkflow",
    "ParsingWorkflowResult",
    "RawParsedDocument",
]

if TYPE_CHECKING:
    from src.application.workflows.parsing.parsing_workflow import ParsingWorkflow
    from src.application.workflows.parsing.parsing_workflow_result import (
        ParsingWorkflowResult,
    )


def __getattr__(name: str):
    if name == "ParsingWorkflow":
        from src.application.workflows.parsing.parsing_workflow import ParsingWorkflow

        return ParsingWorkflow
    if name == "ParsingWorkflowResult":
        from src.application.workflows.parsing.parsing_workflow_result import (
            ParsingWorkflowResult,
        )

        return ParsingWorkflowResult

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
