from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MarkdownTableMetadata:
    caption: str | None = None
    context: str | None = None
    headers: tuple[str, ...] = ()
    row_labels: tuple[str, ...] = ()
    units: tuple[str, ...] = ()
