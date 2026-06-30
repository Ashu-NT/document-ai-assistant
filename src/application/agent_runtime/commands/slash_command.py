from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SlashCommand:
    name: str
    argument_text: str = ""
    raw_text: str = ""

    @property
    def has_argument(self) -> bool:
        return bool(self.argument_text.strip())
