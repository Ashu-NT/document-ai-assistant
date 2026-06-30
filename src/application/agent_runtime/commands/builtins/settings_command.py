from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class SettingsCommand:
    names = ("settings",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        return CommandResult(
            success=True,
            message="Runtime Settings",
            data=agent.build_settings_payload(session),
            render_as="settings",
        )
