from dataclasses import dataclass


@dataclass(slots=True)
class FormField:
    label: str | None
    key_text: str | None
    value_text: str | None
    cell_id: int | None = None
