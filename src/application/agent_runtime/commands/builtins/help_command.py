from __future__ import annotations

from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand


class HelpCommand:
    names = ("help",)

    def execute(self, command: SlashCommand, *, agent, session) -> CommandResult:
        groups = {
            "Documents": [
                {
                    "command": "/list",
                    "description": "List indexed documents available in the corpus.",
                },
                {
                    "command": "/open <document>",
                    "description": "Select a document for follow-up questions and research.",
                },
                {
                    "command": "/current",
                    "description": "Show the document currently selected for this session.",
                },
                {
                    "command": "/close",
                    "description": "Clear the current document selection.",
                },
            ],
            "Conversation": [
                {
                    "command": "/history",
                    "description": "Show the recent conversation turns in this session.",
                },
                {
                    "command": "/reset",
                    "description": "Reset session state, including history and selected document.",
                },
                {
                    "command": "/clear",
                    "description": "Alias for /reset.",
                },
                {
                    "command": "/export",
                    "description": "Export the latest trace as Markdown and JSON.",
                },
            ],
            "Research": [
                {
                    "command": "/trace",
                    "description": "Show the latest safe agent trace for the current session.",
                },
                {
                    "command": "/context",
                    "description": "Show the latest retrieved evidence chunks.",
                },
            ],
            "System": [
                {
                    "command": "/status",
                    "description": "Show runtime status for the current demo session.",
                },
                {
                    "command": "/settings",
                    "description": "Show active runtime options and model configuration.",
                },
                {
                    "command": "/help",
                    "description": "Show the available commands and what they do.",
                },
                {
                    "command": "/exit",
                    "description": "Exit the interactive demo runtime.",
                },
                {
                    "command": "/quit",
                    "description": "Alias for /exit.",
                },
            ],
        }
        examples = []
        if session.runtime_options.help_examples and not session.runtime_options.no_examples:
            examples = [
                "What are the maintenance intervals?",
                "Compare maintenance tasks and specifications.",
                "Find part number A00168.",
            ]
        return CommandResult(
            success=True,
            message="Help",
            data={
                "groups": groups,
                "examples": examples,
            },
            render_as="help",
        )
