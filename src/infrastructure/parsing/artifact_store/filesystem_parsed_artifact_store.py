from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from src.application.workflows.parsing.artifact_store.parsed_artifact_key import (
    ParsedArtifactKey,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.config.logging import get_logger
from src.shared.exceptions import ArtifactStoreError

_logger = get_logger(__name__)

_MANIFEST_FILENAME = "manifest.json"
_DOCUMENT_FILENAME = "document.json"


class FilesystemParsedArtifactStore:
    """Filesystem-backed `ParsedArtifactStorePort`.

    Publication is content-addressed and immutable: a canonical artifact
    lives at ``<root>/<key.cache_key>/`` and, once that directory exists, it
    is never overwritten. Concurrent publishers of the same key each stage
    their own conversion under a uniquely-named directory and race a single
    `os.rename` onto the canonical path; on both Windows and POSIX, renaming
    a directory onto an existing destination fails atomically rather than
    silently replacing it (POSIX `rename(2)` refuses a non-empty
    destination directory; Windows `MoveFileEx` refuses any existing
    destination), so exactly one staged directory ever becomes canonical
    and the loser(s) simply discard their own staging directory. No lock is
    used or needed.
    """

    def __init__(self, root_dir: Path) -> None:
        self._root = root_dir
        self._staging_root = root_dir / ".staging"

    def get(
        self,
        key: ParsedArtifactKey,
        *,
        file_path: str,
    ) -> RawParsedDocument | None:
        artifact_dir = self._artifact_dir(key)
        validation = self._read_and_validate_manifest(artifact_dir, key)
        if validation is None:
            return None
        manifest, document_bytes = validation

        try:
            document_dict = json.loads(document_bytes)
        except json.JSONDecodeError as exc:
            _logger.warning(
                "parsed_artifact_corrupt_document_json cache_key=%s error=%r",
                key.cache_key,
                exc,
            )
            return None

        try:
            raw_document = _docling_document_class().model_validate(document_dict)
        except (ValidationError, TypeError, ValueError) as exc:
            _logger.warning(
                "parsed_artifact_schema_validation_failed cache_key=%s error=%r",
                key.cache_key,
                exc,
            )
            return None

        return RawParsedDocument(
            file_path=file_path,
            title=manifest.get("title"),
            page_count=manifest.get("page_count"),
            raw_document=raw_document,
            parser_name=manifest.get("parser_name") or key.parser_name,
            parser_version=manifest.get("parser_version"),
            metadata=dict(manifest.get("metadata") or {}),
        )

    def put(self, key: ParsedArtifactKey, document: RawParsedDocument) -> None:
        artifact_dir = self._artifact_dir(key)
        if self._read_and_validate_manifest(artifact_dir, key) is not None:
            # Already published (by us or a concurrent publisher) - the
            # canonical artifact is immutable, so there is nothing to do.
            return

        try:
            document_dict = document.raw_document.export_to_dict()
        except Exception as exc:  # noqa: BLE001 - conversion of an already
            # -successful parse's own document must never look like a
            # store failure; surface it distinctly for diagnostics.
            raise ArtifactStoreError(
                "Failed to export raw parsed document for artifact publication.",
                details={"cache_key": key.cache_key},
            ) from exc

        staging_dir = self._staging_root / f"{key.cache_key}-{uuid4().hex}"
        try:
            self._staging_root.mkdir(parents=True, exist_ok=True)
            staging_dir.mkdir(parents=True, exist_ok=False)

            document_bytes = json.dumps(document_dict, indent=2).encode("utf-8")
            document_sha256 = hashlib.sha256(document_bytes).hexdigest()
            _write_bytes_durably(staging_dir / _DOCUMENT_FILENAME, document_bytes)

            manifest = {
                "schema_version": key.schema_version,
                "source_sha256": key.source_sha256,
                "parser_name": key.parser_name,
                "parser_version": key.parser_version,
                "conversion_fingerprint": key.conversion_fingerprint,
                "document_sha256": document_sha256,
                "title": document.title,
                "page_count": document.page_count,
                "metadata": document.metadata,
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
            manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
            _write_bytes_durably(staging_dir / _MANIFEST_FILENAME, manifest_bytes)

            self._root.mkdir(parents=True, exist_ok=True)
        except (OSError, TypeError, ValueError) as exc:
            # OSError: filesystem staging/write failures. TypeError/
            # ValueError: json.dumps() failures (a non-JSON-serializable
            # value reached document_dict/manifest, or a circular
            # reference) - a malformed-but-otherwise-successful parse must
            # degrade to "publication failed" here, not crash the caller.
            self._discard_staging(staging_dir)
            raise ArtifactStoreError(
                "Failed to stage parsed artifact for publication.",
                details={"cache_key": key.cache_key},
            ) from exc

        try:
            os.rename(staging_dir, artifact_dir)
        except OSError as exc:
            if not artifact_dir.exists():
                # Rename failed for a reason unrelated to a publication
                # race (permissions, cross-device link, disk full on the
                # directory entry, ...) - this is a genuine publish
                # failure, not a benign "someone else published first".
                self._discard_staging(staging_dir)
                raise ArtifactStoreError(
                    "Failed to publish parsed artifact: rename to canonical "
                    "path failed and no canonical artifact exists.",
                    details={"cache_key": key.cache_key},
                ) from exc

            # Lost the publication race: some other publisher's rename won.
            # Validate/accept the now-canonical artifact and discard ours.
            if self._read_and_validate_manifest(artifact_dir, key) is None:
                _logger.error(
                    "parsed_artifact_publication_race_unresolved cache_key=%s "
                    "artifact_dir=%s: destination exists but is not a valid "
                    "canonical artifact; leaving it untouched.",
                    key.cache_key,
                    artifact_dir,
                )
            self._discard_staging(staging_dir)

    def _artifact_dir(self, key: ParsedArtifactKey) -> Path:
        return self._root / key.cache_key

    def _read_and_validate_manifest(
        self,
        artifact_dir: Path,
        key: ParsedArtifactKey,
    ) -> tuple[dict[str, Any], bytes] | None:
        manifest_path = artifact_dir / _MANIFEST_FILENAME
        document_path = artifact_dir / _DOCUMENT_FILENAME
        if not manifest_path.is_file() or not document_path.is_file():
            return None

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            _logger.warning(
                "parsed_artifact_manifest_unreadable cache_key=%s error=%r",
                key.cache_key,
                exc,
            )
            return None

        if manifest.get("schema_version") != key.schema_version:
            _logger.warning(
                "parsed_artifact_unsupported_schema cache_key=%s "
                "manifest_schema_version=%r expected=%r",
                key.cache_key,
                manifest.get("schema_version"),
                key.schema_version,
            )
            return None

        try:
            document_bytes = document_path.read_bytes()
        except OSError as exc:
            _logger.warning(
                "parsed_artifact_document_unreadable cache_key=%s error=%r",
                key.cache_key,
                exc,
            )
            return None

        actual_checksum = hashlib.sha256(document_bytes).hexdigest()
        if actual_checksum != manifest.get("document_sha256"):
            _logger.warning(
                "parsed_artifact_checksum_mismatch cache_key=%s",
                key.cache_key,
            )
            return None

        return manifest, document_bytes

    @staticmethod
    def _discard_staging(staging_dir: Path) -> None:
        try:
            shutil.rmtree(staging_dir, ignore_errors=False)
        except OSError as exc:
            _logger.warning(
                "parsed_artifact_staging_cleanup_failed path=%s error=%r",
                staging_dir,
                exc,
            )


def _write_bytes_durably(path: Path, data: bytes) -> None:
    with open(path, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _docling_document_class() -> Any:
    from docling_core.types.doc import DoclingDocument

    return DoclingDocument
