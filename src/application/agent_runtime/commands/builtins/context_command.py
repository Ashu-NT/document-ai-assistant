from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class ContextCommand:
    names = ("context",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        if not session.last_context_chunks:
            return CommandResult(
                success=False,
                message="No retrieved context is available yet.",
            )
        return CommandResult(
            success=True,
            message="Retrieved Context",
            data={"context_chunks": session.last_context_chunks},
            render_as="context",
        )
