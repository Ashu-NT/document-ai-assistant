from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DocumentHashes:
    file_hash: str
    content_hash: str | None = None

    def has_content_hash(self) -> bool:
        return bool(self.content_hash)