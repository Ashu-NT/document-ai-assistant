from __future__ import annotations

import re
from typing import Any

from src.application.agent_runtime.commands.builtins import (
    ClearDocumentCommand,
    ContextCommand,
    CurrentDocumentCommand,
    ExitCommand,
    ExportCommand,
    HelpCommand,
    HistoryCommand,
    ListCommand,
    OpenCommand,
    ResetCommand,
    SettingsCommand,
    StatusCommand,
    TraceCommand,
)
from src.application.agent_runtime.commands.command_result import CommandResult
from src.application.agent_runtime.commands.slash_command import SlashCommand

_SLASH_RE = re.compile(r"^/(?P<name>[a-zA-Z][a-zA-Z0-9_-]*)(?:\s+(?P<args>.*))?$")


class CommandDispatcher:
    def __init__(self) -> None:
        self._handlers = [
            HelpCommand(),
            ListCommand(),
            OpenCommand(),
            CurrentDocumentCommand(),
            ClearDocumentCommand(),
            HistoryCommand(),
            ExportCommand(),
            StatusCommand(),
            SettingsCommand(),
            TraceCommand(),
            ContextCommand(),
            ResetCommand(),
            ExitCommand(),
        ]

    def parse(self, user_input: str) -> SlashCommand | None:
        text = user_input.strip()
        if not text:
            return None
        match = _SLASH_RE.match(text)
        if match is not None:
            return SlashCommand(
                name=match.group("name").strip().lower(),
                argument_text=(match.group("args") or "").strip(),
                raw_text=text,
            )
        normalized = " ".join(text.split()).lower()
        if normalized in {"help"}:
            return SlashCommand(name="help", raw_text=text)
        if normalized in {"list documents", "list docs", "documents"}:
            return SlashCommand(name="list", raw_text=text)
        if normalized in {"current document"}:
            return SlashCommand(name="current", raw_text=text)
        if normalized in {"clear document"}:
            return SlashCommand(name="close", raw_text=text)
        if normalized in {"exit", "quit"}:
            return SlashCommand(name="exit", raw_text=text)
        if normalized.startswith("open "):
            return SlashCommand(
                name="open",
                argument_text=text[5:].strip(),
                raw_text=text,
            )
        return None

    def dispatch(self, user_input: str, *, agent: Any, session) -> CommandResult | None:
        command = self.parse(user_input)
        if command is None:
            return None
        handler = self._resolve_handler(command.name)
        if handler is None:
            return CommandResult(
                success=False,
                message=f"Unknown command: {command.raw_text}",
            )
        return handler.execute(command, agent=agent, session=session)

    def _resolve_handler(self, name: str):
        for handler in self._handlers:
            if name in getattr(handler, "names", ()):
                return handler
        return None
