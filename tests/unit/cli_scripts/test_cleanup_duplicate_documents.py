from __future__ import annotations

import importlib.util
import sys

from datetime import UTC, datetime
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"


def _load_script(script_name: str):
    cached_key = f"_cli_test_{script_name}"
    if cached_key in sys.modules:
        return sys.modules[cached_key]

    script_path = _SCRIPTS_DIR / f"{script_name}.py"
    saved_path = list(sys.path)
    spec = importlib.util.spec_from_file_location(cached_key, script_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[cached_key] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(cached_key, None)
        raise
    finally:
        sys.path[:] = saved_path
    return mod


def _record(mod, *, document_id: str, file_path: str, created_at: datetime, chunk_count: int):
    return mod.DuplicateDocumentRecord(
        document_id=document_id,
        title="Manual",
        file_name=Path(file_path).name,
        file_path=file_path,
        file_hash=f"hash_{document_id}",
        content_hash=f"content_{Path(file_path).name}",
        document_type="manual",
        page_count=10,
        chunk_count=chunk_count,
        created_at=created_at,
    )


def test_cleanup_duplicate_documents_parse_args_defaults() -> None:
    mod = _load_script("cleanup_duplicate_documents")
    args = mod.parse_args([])
    assert args.group_by == "file_path"
    assert args.keep == "oldest"
    assert args.apply is False
    assert args.filter is None


def test_cleanup_duplicate_documents_builds_oldest_keep_plan() -> None:
    mod = _load_script("cleanup_duplicate_documents")
    records = [
        _record(
            mod,
            document_id="doc_old",
            file_path="C:/docs/manual.pdf",
            created_at=datetime(2026, 7, 1, tzinfo=UTC),
            chunk_count=25,
        ),
        _record(
            mod,
            document_id="doc_new",
            file_path="C:/docs/manual.pdf",
            created_at=datetime(2026, 7, 2, tzinfo=UTC),
            chunk_count=30,
        ),
    ]

    plans = mod.build_duplicate_deletion_plans(
        records,
        group_by="file_path",
        keep="oldest",
    )

    assert len(plans) == 1
    assert plans[0].keep_record.document_id == "doc_old"
    assert [record.document_id for record in plans[0].delete_records] == ["doc_new"]
    assert plans[0].warning is not None


def test_cleanup_duplicate_documents_can_keep_newest() -> None:
    mod = _load_script("cleanup_duplicate_documents")
    records = [
        _record(
            mod,
            document_id="doc_old",
            file_path="C:/docs/manual.pdf",
            created_at=datetime(2026, 7, 1, tzinfo=UTC),
            chunk_count=25,
        ),
        _record(
            mod,
            document_id="doc_new",
            file_path="C:/docs/manual.pdf",
            created_at=datetime(2026, 7, 2, tzinfo=UTC),
            chunk_count=30,
        ),
    ]

    plans = mod.build_duplicate_deletion_plans(
        records,
        group_by="file_path",
        keep="newest",
    )

    assert len(plans) == 1
    assert plans[0].keep_record.document_id == "doc_new"
    assert [record.document_id for record in plans[0].delete_records] == ["doc_old"]
    assert plans[0].warning is None


def test_cleanup_duplicate_documents_skips_groups_without_key() -> None:
    mod = _load_script("cleanup_duplicate_documents")
    records = [
        mod.DuplicateDocumentRecord(
            document_id="doc_1",
            title="Manual",
            file_name="manual.pdf",
            file_path="C:/docs/manual.pdf",
            file_hash="hash_1",
            content_hash=None,
            document_type="manual",
            page_count=10,
            chunk_count=20,
            created_at=datetime(2026, 7, 1, tzinfo=UTC),
        ),
        mod.DuplicateDocumentRecord(
            document_id="doc_2",
            title="Manual",
            file_name="manual.pdf",
            file_path="C:/docs/manual.pdf",
            file_hash="hash_2",
            content_hash=None,
            document_type="manual",
            page_count=10,
            chunk_count=20,
            created_at=datetime(2026, 7, 2, tzinfo=UTC),
        ),
    ]

    plans = mod.build_duplicate_deletion_plans(
        records,
        group_by="content_hash",
        keep="oldest",
    )

    assert plans == []
