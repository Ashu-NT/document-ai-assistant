from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class ExportCommand:
    names = ("export",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        export_paths = agent.export_latest_trace(session)
        if export_paths is None:
            return CommandResult(
                success=False,
                message="No trace is available to export yet.",
            )
        return CommandResult(
            success=True,
            message="Trace saved:",
            data=export_paths,
            render_as="export",
        )
