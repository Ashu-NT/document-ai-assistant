from __future__ import annotations

from typing import Any

from src.application.validation.common import ValidationResult, Validator


class GraphStateValidator(Validator[dict[str, Any]]):
    def validate(self, value: dict[str, Any]) -> ValidationResult:
        result = ValidationResult()

        selected_document_id = value.get("selected_document_id")
        selected_document_title = value.get("selected_document_title")
        selected_document_file_name = value.get("selected_document_file_name")
        if selected_document_id is None and (
            selected_document_title is not None or selected_document_file_name is not None
        ):
            result.add_issue(
                "selected_document_id",
                "selected document title/file name cannot exist without selected_document_id.",
                "langgraph.selected_document.missing_id",
            )

        pending_clarification = value.get("pending_clarification")
        clarification_options = value.get("clarification_options", [])
        clarification_question = value.get("clarification_question")
        if pending_clarification is not None and not isinstance(pending_clarification, dict):
            result.add_issue(
                "pending_clarification",
                "pending_clarification must be a dictionary when provided.",
                "langgraph.pending_clarification.invalid_type",
            )

        if clarification_options is not None and not isinstance(clarification_options, list):
            result.add_issue(
                "clarification_options",
                "clarification_options must be a list when provided.",
                "langgraph.clarification_options.invalid_type",
            )

        if not isinstance(clarification_options, list):
            clarification_options = []

        if isinstance(clarification_options, list):
            for index, option in enumerate(clarification_options):
                if not isinstance(option, dict):
                    result.add_issue(
                        f"clarification_options[{index}]",
                        "Each clarification option must be a dictionary.",
                        "langgraph.clarification_options.invalid_entry",
                    )

        if (pending_clarification or clarification_question) and not clarification_options:
            result.add_issue(
                "clarification_options",
                "Clarification state requires at least one clarification option.",
                "langgraph.clarification_options.required",
            )

        clarification_candidate_index = value.get("clarification_candidate_index")
        if clarification_candidate_index is not None:
            if not isinstance(clarification_candidate_index, int):
                result.add_issue(
                    "clarification_candidate_index",
                    "clarification_candidate_index must be an integer when provided.",
                    "langgraph.clarification_candidate_index.invalid_type",
                )
            elif clarification_candidate_index < 0 or clarification_candidate_index >= len(
                clarification_options
            ):
                result.add_issue(
                    "clarification_candidate_index",
                    "clarification_candidate_index is out of range for clarification_options.",
                    "langgraph.clarification_candidate_index.out_of_range",
                )

        return result
