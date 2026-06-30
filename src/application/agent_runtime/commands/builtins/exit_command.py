from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class ExitCommand:
    names = ("exit", "quit")

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        return CommandResult(
            success=True,
            message="Exiting document agent.",
            should_exit=True,
        )
