from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DocumentHashes:
    file_hash: str
    content_hash: str | None = None