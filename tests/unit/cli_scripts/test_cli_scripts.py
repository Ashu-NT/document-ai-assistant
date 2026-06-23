"""
Lightweight smoke tests for the CLI scripts.

Verifies argparse configuration and that script modules load without triggering
any database, Qdrant, or model connections.

sys.path is saved and restored around each script import so that module-level
path additions in the scripts do not affect import resolution in other test files.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"


def _load_script(script_name: str):
    """
    Load a script from scripts/ by name, restoring sys.path afterwards.

    The CLI scripts add PROJECT_ROOT / SRC_ROOT to sys.path at module level
    so their deferred imports work when run standalone.  When imported via
    tests those insertions change import resolution for other test files.
    We isolate the side-effect by restoring sys.path after exec_module.
    """
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
        sys.path[:] = saved_path  # undo any sys.path inserts the script made
    return mod


# ---------------------------------------------------------------------------
# list_documents.py
# ---------------------------------------------------------------------------


def test_list_documents_module_importable():
    mod = _load_script("list_documents")
    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "main")


def test_list_documents_parse_args_defaults():
    mod = _load_script("list_documents")
    args = mod.parse_args([])
    assert args.json is False


def test_list_documents_parse_args_json_flag():
    mod = _load_script("list_documents")
    args = mod.parse_args(["--json"])
    assert args.json is True


def test_list_documents_trunc_short():
    mod = _load_script("list_documents")
    assert mod._trunc("hello", 10) == "hello"


def test_list_documents_trunc_long():
    mod = _load_script("list_documents")
    result = mod._trunc("a" * 30, 10)
    assert len(result) == 10
    assert result.endswith("...")


def test_list_documents_trunc_none():
    mod = _load_script("list_documents")
    assert mod._trunc(None, 10) == "-"


# ---------------------------------------------------------------------------
# ask_document.py
# ---------------------------------------------------------------------------


def test_ask_document_module_importable():
    mod = _load_script("ask_document")
    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "main")


def test_ask_document_parse_args_positional():
    mod = _load_script("ask_document")
    args = mod.parse_args(["What is the maintenance interval?", "--latest"])
    assert args.question_positional == "What is the maintenance interval?"
    assert args.latest is True
    assert args.generate is False


def test_ask_document_parse_args_flag_question():
    mod = _load_script("ask_document")
    args = mod.parse_args(
        ["--question", "How do I change the oil?", "--document", "Engine"]
    )
    assert args.question == "How do I change the oil?"
    assert args.document == "Engine"


def test_ask_document_parse_args_generate():
    mod = _load_script("ask_document")
    args = mod.parse_args(["What is X?", "--latest", "--generate"])
    assert args.generate is True


def test_ask_document_parse_args_top_k():
    mod = _load_script("ask_document")
    args = mod.parse_args(["Q?", "--latest", "--top-k", "7"])
    assert args.top_k == 7


def test_ask_document_parse_args_show_context():
    mod = _load_script("ask_document")
    args = mod.parse_args(["Q?", "--latest", "--show-context"])
    assert args.show_context is True


def test_ask_document_parse_args_json():
    mod = _load_script("ask_document")
    args = mod.parse_args(["Q?", "--latest", "--json"])
    assert args.json is True


def test_ask_document_parse_args_document_id():
    mod = _load_script("ask_document")
    args = mod.parse_args(["Q?", "--document-id", "abc-123"])
    assert args.document_id == "abc-123"
    assert args.document is None
    assert args.latest is False


def test_ask_document_document_flags_mutually_exclusive():
    mod = _load_script("ask_document")
    with pytest.raises(SystemExit):
        mod.parse_args(["Q?", "--document-id", "abc", "--latest"])


def test_ask_document_resolve_question_positional():
    mod = _load_script("ask_document")
    args = mod.parse_args(["My question", "--latest"])
    assert mod.resolve_question(args) == "My question"


def test_ask_document_resolve_question_flag():
    mod = _load_script("ask_document")
    args = mod.parse_args(["--question", "My question", "--latest"])
    assert mod.resolve_question(args) == "My question"


def test_ask_document_main_no_question_returns_1():
    mod = _load_script("ask_document")
    result = mod.main([])
    assert result == 1


def test_ask_document_page_range_with_pages():
    mod = _load_script("ask_document")
    source = MagicMock()
    source.page_start = 10
    source.page_end = 12
    assert mod._page_range(source) == "pages 10-12"


def test_ask_document_page_range_single_page():
    mod = _load_script("ask_document")
    source = MagicMock()
    source.page_start = 5
    source.page_end = 5
    assert mod._page_range(source) == "page 5"


def test_ask_document_page_range_no_page():
    mod = _load_script("ask_document")
    source = MagicMock()
    source.page_start = None
    assert mod._page_range(source) == ""
