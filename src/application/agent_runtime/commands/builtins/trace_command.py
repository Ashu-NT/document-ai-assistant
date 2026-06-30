from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class TraceCommand:
    names = ("trace",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        if session.last_trace is None:
            return CommandResult(
                success=False,
                message="No trace is available yet.",
            )
        return CommandResult(
            success=True,
            message="Agent Trace",
            data={"trace": session.last_trace},
            render_as="trace",
        )
