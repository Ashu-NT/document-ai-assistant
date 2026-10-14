import json

from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.batching.extraction_family_response_keys import (
    omitted_requested_family_keys,
)


def test_none_requested_types_returns_empty() -> None:
    assert omitted_requested_family_keys(None, "{}") == ()


def test_key_present_as_empty_array_is_not_reported_omitted() -> None:
    response = json.dumps({"maintenance_tasks": []})

    result = omitted_requested_family_keys(
        frozenset({ExtractionPromptType.MAINTENANCE_TASK}), response
    )

    assert result == ()


def test_key_textually_absent_is_reported_omitted() -> None:
    response = json.dumps({"identifiers": []})

    result = omitted_requested_family_keys(
        frozenset({ExtractionPromptType.MAINTENANCE_TASK, ExtractionPromptType.IDENTIFIER}),
        response,
    )

    assert result == ("maintenance_tasks",)


def test_degenerate_empty_object_reports_every_requested_family() -> None:
    result = omitted_requested_family_keys(
        frozenset({ExtractionPromptType.MAINTENANCE_TASK, ExtractionPromptType.PROCEDURE}),
        "{ \n\n  \t\t}",
    )

    assert result == ("maintenance_tasks", "procedures")
