from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class ClearDocumentCommand:
    names = ("close",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        result = agent.execute_graph_command("clear document", session=session)
        return CommandResult(
            success=result.success,
            message="Cleared selected document." if result.success else (result.response_text or "Failed to clear document."),
            data={"graph_result": result},
            update_session=True,
        )
