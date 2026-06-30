from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class ListCommand:
    names = ("list",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        result = agent.execute_graph_command("list documents", session=session)
        documents = agent.extract_list_documents(result)
        return CommandResult(
            success=result.success,
            message="Indexed Documents",
            data={
                "graph_result": result,
                "documents": documents,
            },
            update_session=True,
            render_as="documents",
        )
