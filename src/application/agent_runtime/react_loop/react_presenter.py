from __future__ import annotations

from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.react_loop.react_trace import ReactTrace
from src.shared.text.text_preview import truncate_at_word_boundary


class ReactPresenter:
    def render(self, trace: ReactTrace, *, policy: DemoVisibilityPolicy) -> str:
        if trace.is_empty():
            return ""
        title = "Debug Trace" if policy.debug else "Agent Trace"
        lines = [
            title,
            "----------------------------------------------------------------------",
            "",
        ]
        for step in trace.steps:
            body = step.body.strip()
            if not body:
                continue
            if len(body) > policy.max_step_chars:
                # finding 6.10: break at the last whitespace boundary before
                # the limit instead of a raw character slice, so truncation
                # doesn't cut a word (or a safety warning) in half.
                body = (
                    truncate_at_word_boundary(body, policy.max_step_chars - 3)
                    + "..."
                )
            lines.append(f"[{step.index}] {step.title}")
            lines.append(body)
            lines.append("")
        return "\n".join(lines).rstrip()
