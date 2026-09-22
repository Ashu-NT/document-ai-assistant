import hashlib

import pytest

from src.application.evaluation.corpus import (
    GoldenCorpusManifest,
    GoldenDocumentAvailability,
    GoldenDocumentManifestEntry,
)
from src.domain.common import DocumentType
from src.shared.exceptions import SchemaValidationError


def _write(path, content: bytes = b"dummy content") -> str:
    path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


class TestAliasResolution:
    def test_resolve_is_independent_of_absolute_machine_path(self, tmp_path) -> None:
        # Two different manifests pointing at two different roots for the
        # SAME relative_path/alias must resolve to each machine's own
        # absolute path - the alias is the portable identity, not any one
        # machine's path.
        (tmp_path / "root_a").mkdir()
        (tmp_path / "root_b").mkdir()
        digest = _write(tmp_path / "root_a" / "doc.pdf")
        _write(tmp_path / "root_b" / "doc.pdf")

        entry = GoldenDocumentManifestEntry(
            alias="doc_x", relative_path="doc.pdf", category="manual"
        )
        manifest_a = GoldenCorpusManifest([entry], root_dir=tmp_path / "root_a")
        manifest_b = GoldenCorpusManifest([entry], root_dir=tmp_path / "root_b")

        resolved_a = manifest_a.resolve("doc_x")
        resolved_b = manifest_b.resolve("doc_x")

        assert resolved_a.absolute_path == tmp_path / "root_a" / "doc.pdf"
        assert resolved_b.absolute_path == tmp_path / "root_b" / "doc.pdf"
        assert resolved_a.alias == resolved_b.alias == "doc_x"
        assert resolved_a.availability == GoldenDocumentAvailability.AVAILABLE

    def test_unknown_alias_raises(self, tmp_path) -> None:
        manifest = GoldenCorpusManifest([], root_dir=tmp_path)

        with pytest.raises(SchemaValidationError):
            manifest.entry("does_not_exist")

    def test_duplicate_alias_raises_at_construction(self, tmp_path) -> None:
        entries = [
            GoldenDocumentManifestEntry(alias="dup", relative_path="a.pdf", category="manual"),
            GoldenDocumentManifestEntry(alias="dup", relative_path="b.pdf", category="manual"),
        ]

        with pytest.raises(SchemaValidationError):
            GoldenCorpusManifest(entries, root_dir=tmp_path)


class TestAvailability:
    def test_missing_document_is_explicit(self, tmp_path) -> None:
        entry = GoldenDocumentManifestEntry(
            alias="doc_x", relative_path="does_not_exist.pdf", category="manual"
        )
        manifest = GoldenCorpusManifest([entry], root_dir=tmp_path)

        resolved = manifest.resolve("doc_x")

        assert resolved.availability == GoldenDocumentAvailability.MISSING
        assert resolved.is_available is False
        assert resolved.actual_sha256 is None

    def test_expected_sha_mismatch_is_detected(self, tmp_path) -> None:
        _write(tmp_path / "doc.pdf", b"real content")
        entry = GoldenDocumentManifestEntry(
            alias="doc_x",
            relative_path="doc.pdf",
            category="manual",
            expected_sha256="0" * 64,
        )
        manifest = GoldenCorpusManifest([entry], root_dir=tmp_path)

        resolved = manifest.resolve("doc_x")

        assert resolved.availability == GoldenDocumentAvailability.HASH_MISMATCH
        assert resolved.is_available is False
        assert resolved.actual_sha256 is not None
        assert resolved.actual_sha256 != entry.expected_sha256

    def test_matching_sha_is_available(self, tmp_path) -> None:
        digest = _write(tmp_path / "doc.pdf", b"real content")
        entry = GoldenDocumentManifestEntry(
            alias="doc_x", relative_path="doc.pdf", category="manual", expected_sha256=digest
        )
        manifest = GoldenCorpusManifest([entry], root_dir=tmp_path)

        resolved = manifest.resolve("doc_x")

        assert resolved.availability == GoldenDocumentAvailability.AVAILABLE
        assert resolved.actual_sha256 == digest

    def test_no_expected_sha_is_available_regardless_of_content(self, tmp_path) -> None:
        _write(tmp_path / "doc.pdf", b"anything")
        entry = GoldenDocumentManifestEntry(
            alias="doc_x", relative_path="doc.pdf", category="manual", expected_sha256=None
        )
        manifest = GoldenCorpusManifest([entry], root_dir=tmp_path)

        resolved = manifest.resolve("doc_x")

        assert resolved.availability == GoldenDocumentAvailability.AVAILABLE

    def test_resolve_all_covers_every_entry_explicitly(self, tmp_path) -> None:
        _write(tmp_path / "present.pdf")
        entries = [
            GoldenDocumentManifestEntry(alias="present", relative_path="present.pdf", category="manual"),
            GoldenDocumentManifestEntry(alias="absent", relative_path="absent.pdf", category="manual"),
        ]
        manifest = GoldenCorpusManifest(entries, root_dir=tmp_path)

        resolved_all = manifest.resolve_all()

        assert {r.alias for r in resolved_all} == {"present", "absent"}
        statuses = {r.alias: r.availability for r in resolved_all}
        assert statuses["present"] == GoldenDocumentAvailability.AVAILABLE
        assert statuses["absent"] == GoldenDocumentAvailability.MISSING


class TestDefaultManifest:
    def test_default_manifest_has_ten_documents_with_distinct_aliases(self) -> None:
        manifest = GoldenCorpusManifest.default()

        assert len(manifest.entries) == 10
        assert len({entry.alias for entry in manifest.entries}) == 10

    def test_default_manifest_entries_declare_a_real_production_document_type(self) -> None:
        manifest = GoldenCorpusManifest.default()

        for entry in manifest.entries:
            assert entry.expected_document_type is None or isinstance(
                entry.expected_document_type, DocumentType
            )
