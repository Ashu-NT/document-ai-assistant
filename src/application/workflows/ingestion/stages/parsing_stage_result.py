from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.parsing import ParsingWorkflowResult


@dataclass(slots=True)
class ParsingStageResult:
    parsing_result: ParsingWorkflowResult
    content_hash: str
    parser_name: str | None
    parser_version: str | None
