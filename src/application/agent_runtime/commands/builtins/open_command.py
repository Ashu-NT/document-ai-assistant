from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class OpenCommand:
    names = ("open",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        query = command.argument_text.strip()
        if not query:
            return CommandResult(
                success=False,
                message="Usage: /open <document>",
            )
        result = agent.execute_graph_command(f"open {query}", session=session)
        selected_document = agent.extract_selected_document(result)
        return CommandResult(
            success=result.success,
            message="Selected document" if result.success else (result.response_text or "Document selection failed."),
            data={
                "graph_result": result,
                "selected_document": selected_document,
            },
            update_session=True,
            render_as="document_selected",
        )
