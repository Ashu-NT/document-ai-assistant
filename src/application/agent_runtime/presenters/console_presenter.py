from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.presenters.console.command_result_renderer import (
    render_command_result,
)
from src.application.agent_runtime.presenters.console.graph_result_renderer import (
    render_graph_result,
)
from src.application.agent_runtime.react_loop.react_presenter import ReactPresenter
from src.application.agent_runtime.react_loop.react_trace import ReactTrace


class ConsolePresenter:
    def __init__(self, react_presenter: ReactPresenter | None = None) -> None:
        self.react_presenter = react_presenter or ReactPresenter()

    def render_command_result(
        self,
        result: CommandResult,
        *,
        session,
        policy: DemoVisibilityPolicy,
    ) -> str:
        return render_command_result(
            result,
            session=session,
            policy=policy,
            react_presenter=self.react_presenter,
        )

    def render_graph_result(
        self,
        *,
        user_input: str,
        result,
        react_trace: ReactTrace | None,
        session,
        policy: DemoVisibilityPolicy,
        show_react: bool,
    ) -> str:
        return render_graph_result(
            user_input=user_input,
            result=result,
            react_trace=react_trace,
            session=session,
            policy=policy,
            show_react=show_react,
            react_presenter=self.react_presenter,
        )
