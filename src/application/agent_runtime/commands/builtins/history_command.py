from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class HistoryCommand:
    names = ("history",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        turns = session.conversation_history.turns
        if not turns:
            return CommandResult(
                success=True,
                message="No conversation history yet.",
            )
        return CommandResult(
            success=True,
            message="Conversation History",
            data={"turns": turns},
            render_as="history",
        )
