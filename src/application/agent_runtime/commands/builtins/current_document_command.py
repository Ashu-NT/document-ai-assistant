from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class CurrentDocumentCommand:
    names = ("current",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        selected = session.selected_document.display_name
        if not selected:
            return CommandResult(
                success=True,
                message="No document is currently selected.",
            )
        return CommandResult(
            success=True,
            message="Current document:",
            data={"document_name": selected},
            render_as="current_document",
        )
