from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class StatusCommand:
    names = ("status",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        return CommandResult(
            success=True,
            message="Runtime Status",
            data=agent.build_status_payload(session),
            render_as="status",
        )
