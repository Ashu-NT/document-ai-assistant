from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class ResetCommand:
    names = ("reset", "clear")

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        agent.reset_session(session)
        return CommandResult(
            success=True,
            message="Session history and document selection were cleared.",
        )
