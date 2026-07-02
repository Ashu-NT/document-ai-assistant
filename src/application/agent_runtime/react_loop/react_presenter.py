from __future__ import annotations

from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.react_loop.react_trace import ReactTrace


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
                body = body[: policy.max_step_chars - 3] + "..."
            lines.append(f"[{step.index}] {step.title}")
            lines.append(body)
            lines.append("")
        return "\n".join(lines).rstrip()
