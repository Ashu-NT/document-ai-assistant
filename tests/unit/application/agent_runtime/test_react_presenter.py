from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.react_loop.react_event import ReactEvent
from src.application.agent_runtime.react_loop.react_presenter import ReactPresenter
from src.application.agent_runtime.react_loop.react_trace import ReactTrace, ReactStep


def test_react_presenter_truncates_long_step_body_at_word_boundary() -> None:
    """finding 6.10: truncation must break at a whitespace boundary, not
    mid-word, so a cut-off step body (e.g. a safety warning) doesn't read
    as a mangled half-word."""
    policy = DemoVisibilityPolicy(max_step_chars=40)
    long_body = (
        "Retrieved evidence about the maintenance interval schedule and the "
        "lubrication procedure for the primary drive shaft assembly."
    )
    trace = ReactTrace(
        route="answer_question",
        steps=[
            ReactStep(
                index=1,
                event_type=ReactEvent.THOUGHT_SUMMARY,
                title="Thought Summary",
                body=long_body,
            )
        ],
    )

    rendered = ReactPresenter().render(trace, policy=policy)

    lines = rendered.splitlines()
    body_line = next(line for line in lines if line.startswith("Retrieved"))
    assert body_line.endswith("...")
    trimmed = body_line[: -len("...")]
    assert long_body.startswith(trimmed)
    # Whatever character follows the retained prefix in the source text
    # must be a word boundary -- proving the cut didn't split a word.
    if len(trimmed) < len(long_body):
        assert long_body[len(trimmed)] == " "


def test_react_presenter_short_body_not_truncated() -> None:
    policy = DemoVisibilityPolicy()
    trace = ReactTrace(
        route="answer_question",
        steps=[
            ReactStep(
                index=1,
                event_type=ReactEvent.THOUGHT_SUMMARY,
                title="Thought Summary",
                body="Short body.",
            )
        ],
    )

    rendered = ReactPresenter().render(trace, policy=policy)

    assert "Short body." in rendered
    assert "..." not in rendered
