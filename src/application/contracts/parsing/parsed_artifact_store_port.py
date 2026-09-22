from typing import Protocol

from src.application.workflows.parsing.artifact_store.parsed_artifact_key import (
    ParsedArtifactKey,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument


class ParsedArtifactStorePort(Protocol):
    """Content-addressed checkpoint for `RawParsedDocument` conversions.

    `get()` is authoritative: it must fully validate any candidate artifact
    (existence, schema version, checksum, deserialization) and return
    `None` for anything it cannot trust, rather than raising. A `None`
    result means "reconstruct via normal parsing" - it does not imply an
    infrastructure failure.

    `put()` is a best-effort checkpoint of an already-successful parse. It
    may raise `ArtifactStoreError` on genuine publication failure (disk
    full, permissions, staging/write failure); callers must treat that as
    non-fatal to the parse that produced `document`.
    """

    def get(
        self,
        key: ParsedArtifactKey,
        *,
        file_path: str,
    ) -> RawParsedDocument | None:
        ...

    def put(self, key: ParsedArtifactKey, document: RawParsedDocument) -> None:
        ...
