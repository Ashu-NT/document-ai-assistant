from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from docling_core.types.doc import DocItemLabel, DoclingDocument, GroupLabel
from docling_core.types.doc.base import Size
from docling_core.types.doc.document import TableCell, TableData

from src.application.workflows.parsing.artifact_store.parsed_artifact_key import (
    ParsedArtifactKey,
)
from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.infrastructure.parsing.artifact_store.filesystem_parsed_artifact_store import (
    FilesystemParsedArtifactStore,
)
from src.shared.exceptions import ArtifactStoreError


def _build_docling_document(marker: str) -> DoclingDocument:
    """A genuine DoclingDocument (built through docling-core's own supported
    builder API, not a hand-rolled fake), with a page, a heading, a group
    with two child list items, a table, and a picture - enough surface area
    to prove `export_to_dict()` -> `model_validate()` round-trips pages,
    item counts/types, tables, pictures, group labels, and group-child
    refs/order faithfully."""
    doc = DoclingDocument(name=marker)
    doc.add_page(page_no=1, size=Size(width=612.0, height=792.0))
    doc.add_page(page_no=2, size=Size(width=595.0, height=842.0))
    doc.add_heading(text=f"{marker} Section 1", level=1)
    group = doc.add_group(label=GroupLabel.LIST, name=f"{marker}-list")
    doc.add_text(label=DocItemLabel.LIST_ITEM, text=f"{marker} item one", parent=group)
    doc.add_text(label=DocItemLabel.LIST_ITEM, text=f"{marker} item two", parent=group)
    table_data = TableData(
        num_rows=1,
        num_cols=2,
        table_cells=[
            TableCell(
                text=f"{marker}-a",
                start_row_offset_idx=0,
                end_row_offset_idx=1,
                start_col_offset_idx=0,
                end_col_offset_idx=1,
            ),
            TableCell(
                text=f"{marker}-b",
                start_row_offset_idx=0,
                end_row_offset_idx=1,
                start_col_offset_idx=1,
                end_col_offset_idx=2,
            ),
        ],
    )
    doc.add_table(data=table_data)
    doc.add_picture()
    return doc


def _build_raw_parsed_document(marker: str) -> RawParsedDocument:
    return RawParsedDocument(
        file_path=f"data/input/{marker}_original.pdf",
        title=f"{marker} title",
        page_count=2,
        raw_document=_build_docling_document(marker),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"status": "success"},
    )


def _build_key(*, source_sha256: str = "source-hash", conversion_fingerprint: str = "fp-1") -> ParsedArtifactKey:
    return ParsedArtifactKey(
        source_sha256=source_sha256,
        parser_name="docling",
        parser_version="1.2.3",
        conversion_fingerprint=conversion_fingerprint,
    )


def _structural_fingerprint(doc: DoclingDocument) -> dict:
    return {
        "page_count": len(doc.pages),
        "page_sizes": sorted(
            (page_no, page.size.width, page.size.height)
            for page_no, page in doc.pages.items()
        ),
        "item_labels_in_order": [
            getattr(item, "label", None).value
            if hasattr(getattr(item, "label", None), "value")
            else str(getattr(item, "label", None))
            for item, _level in doc.iterate_items(with_groups=True)
        ],
        "table_count": len(doc.tables),
        "table_cell_texts": [
            sorted(cell.text for cell in table.data.table_cells) for table in doc.tables
        ],
        "picture_count": len(doc.pictures),
        "group_labels": [group.label.value for group in doc.groups],
        "group_children_refs": [
            [child.cref for child in group.children] for group in doc.groups
        ],
    }


class TestRoundTripFidelity:
    def test_put_then_get_preserves_full_docling_structure(self, tmp_path: Path) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        original_document = _build_raw_parsed_document("ROUNDTRIP")
        original_fingerprint = _structural_fingerprint(original_document.raw_document)

        store.put(key, original_document)
        loaded = store.get(key, file_path="data/input/current.pdf")

        assert loaded is not None
        loaded_fingerprint = _structural_fingerprint(loaded.raw_document)
        assert loaded_fingerprint == original_fingerprint
        assert (
            loaded.raw_document.export_to_dict()
            == original_document.raw_document.export_to_dict()
        )


class TestGetMissSemantics:
    def test_get_returns_none_when_nothing_published(self, tmp_path: Path) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()

        assert store.get(key, file_path="data/input/any.pdf") is None

    def test_get_uses_current_invocation_file_path_not_cached_original(
        self, tmp_path: Path
    ) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        store.put(key, _build_raw_parsed_document("PATHTEST"))

        loaded = store.get(key, file_path="data/input/current_invocation.pdf")

        assert loaded is not None
        assert loaded.file_path == "data/input/current_invocation.pdf"

    def test_get_returns_none_for_different_source_hash(self, tmp_path: Path) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        store.put(_build_key(source_sha256="hash-a"), _build_raw_parsed_document("A"))

        assert store.get(_build_key(source_sha256="hash-b"), file_path="x.pdf") is None

    def test_get_returns_none_when_conversion_fingerprint_differs(
        self, tmp_path: Path
    ) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        store.put(
            _build_key(conversion_fingerprint="fp-old"),
            _build_raw_parsed_document("CFG"),
        )

        assert (
            store.get(_build_key(conversion_fingerprint="fp-new"), file_path="x.pdf")
            is None
        )

    def test_get_returns_none_when_manifest_schema_version_is_unsupported(
        self, tmp_path: Path
    ) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        store.put(key, _build_raw_parsed_document("SCHEMA"))

        manifest_path = tmp_path / "artifacts" / key.cache_key / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["schema_version"] = 999
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        assert store.get(key, file_path="x.pdf") is None

    def test_get_returns_none_for_checksum_mismatch(self, tmp_path: Path) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        store.put(key, _build_raw_parsed_document("CHECKSUM"))

        document_path = tmp_path / "artifacts" / key.cache_key / "document.json"
        tampered = document_path.read_bytes() + b" "
        document_path.write_bytes(tampered)

        assert store.get(key, file_path="x.pdf") is None

    def test_get_returns_none_for_corrupted_document_json(self, tmp_path: Path) -> None:
        import hashlib

        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        store.put(key, _build_raw_parsed_document("CORRUPT"))

        artifact_dir = tmp_path / "artifacts" / key.cache_key
        corrupted_bytes = b"{not valid json"
        (artifact_dir / "document.json").write_bytes(corrupted_bytes)
        manifest_path = artifact_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["document_sha256"] = hashlib.sha256(corrupted_bytes).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        assert store.get(key, file_path="x.pdf") is None

    def test_get_returns_none_for_unsupported_document_shape(self, tmp_path: Path) -> None:
        import hashlib

        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        store.put(key, _build_raw_parsed_document("UNSUPPORTED"))

        artifact_dir = tmp_path / "artifacts" / key.cache_key
        # Valid JSON, but not a shape DoclingDocument.model_validate accepts.
        bad_bytes = json.dumps({"totally": "unrelated"}).encode("utf-8")
        (artifact_dir / "document.json").write_bytes(bad_bytes)
        manifest_path = artifact_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["document_sha256"] = hashlib.sha256(bad_bytes).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        assert store.get(key, file_path="x.pdf") is None


class TestPublicationSemantics:
    def test_put_is_a_noop_when_key_already_published(self, tmp_path: Path) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        store.put(key, _build_raw_parsed_document("FIRST"))
        first_manifest = (
            tmp_path / "artifacts" / key.cache_key / "manifest.json"
        ).read_text(encoding="utf-8")

        # A second, distinct document under the *same* key must not
        # overwrite the already-published canonical artifact.
        store.put(key, _build_raw_parsed_document("SECOND"))
        second_manifest = (
            tmp_path / "artifacts" / key.cache_key / "manifest.json"
        ).read_text(encoding="utf-8")

        assert first_manifest == second_manifest

    def test_put_raises_artifact_store_error_and_leaves_no_canonical_artifact(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        from src.infrastructure.parsing.artifact_store import (
            filesystem_parsed_artifact_store,
        )

        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()

        def _boom(path, data) -> None:
            raise OSError("simulated disk failure")

        monkeypatch.setattr(
            filesystem_parsed_artifact_store, "_write_bytes_durably", _boom
        )

        with pytest.raises(ArtifactStoreError):
            store.put(key, _build_raw_parsed_document("FAILS"))

        assert not (tmp_path / "artifacts" / key.cache_key).exists()
        staging_root = tmp_path / "artifacts" / ".staging"
        leftover = list(staging_root.glob("*")) if staging_root.exists() else []
        assert leftover == []

    def test_put_raises_artifact_store_error_when_metadata_is_not_json_serializable(
        self, tmp_path: Path
    ) -> None:
        # Regression test: a real Docling parse's RawParsedDocument.metadata
        # can legitimately contain a value that turns out not to be
        # JSON-serializable (discovered via a real 98-page manual: Docling's
        # ConfidenceReport landing in metadata unconverted). This must
        # degrade to ArtifactStoreError, never a raw TypeError/ValueError
        # escaping put() - a malformed-but-otherwise-successful parse must
        # never crash the caller.
        import dataclasses

        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        document = dataclasses.replace(
            _build_raw_parsed_document("BADMETA"),
            metadata={"confidence": {1, 2, 3}},  # a set: not JSON-serializable
        )

        with pytest.raises(ArtifactStoreError):
            store.put(key, document)

        # No partially published canonical artifact is visible.
        assert not (tmp_path / "artifacts" / key.cache_key).exists()
        # Staging data was cleaned up per the existing publication contract.
        staging_root = tmp_path / "artifacts" / ".staging"
        leftover = list(staging_root.glob("*")) if staging_root.exists() else []
        assert leftover == []

    def test_concurrent_same_key_publication_yields_one_valid_canonical_artifact(
        self, tmp_path: Path
    ) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key = _build_key()
        expected_fingerprint = _structural_fingerprint(
            _build_docling_document("RACE")
        )

        def _publish(worker_index: int) -> None:
            store.put(key, _build_raw_parsed_document("RACE"))

        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(_publish, range(8)))

        artifacts_root = tmp_path / "artifacts"
        published_dirs = [
            child
            for child in artifacts_root.iterdir()
            if child.is_dir() and child.name != ".staging"
        ]
        assert len(published_dirs) == 1
        assert published_dirs[0].name == key.cache_key

        loaded = store.get(key, file_path="data/input/race.pdf")
        assert loaded is not None
        assert _structural_fingerprint(loaded.raw_document) == expected_fingerprint

        staging_root = artifacts_root / ".staging"
        leftover = list(staging_root.glob("*")) if staging_root.exists() else []
        assert leftover == []

    def test_concurrent_different_key_publication_are_independent(
        self, tmp_path: Path
    ) -> None:
        store = FilesystemParsedArtifactStore(root_dir=tmp_path / "artifacts")
        key_a = _build_key(source_sha256="hash-a")
        key_b = _build_key(source_sha256="hash-b")

        def _publish(marker_and_key: tuple[str, ParsedArtifactKey]) -> None:
            marker, key = marker_and_key
            store.put(key, _build_raw_parsed_document(marker))

        jobs = [("ALPHA", key_a), ("BRAVO", key_b)] * 4
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(_publish, jobs))

        loaded_a = store.get(key_a, file_path="a.pdf")
        loaded_b = store.get(key_b, file_path="b.pdf")

        assert loaded_a is not None
        assert loaded_b is not None
        assert _structural_fingerprint(loaded_a.raw_document) == _structural_fingerprint(
            _build_docling_document("ALPHA")
        )
        assert _structural_fingerprint(loaded_b.raw_document) == _structural_fingerprint(
            _build_docling_document("BRAVO")
        )
