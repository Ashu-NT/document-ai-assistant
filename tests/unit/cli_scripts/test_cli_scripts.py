"""
Lightweight smoke tests for the CLI scripts.

These tests verify argparse configuration and that the script modules can be
imported without triggering any database, Qdrant, or model connections.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/ is importable
_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# list_documents.py
# ---------------------------------------------------------------------------


def _import_list_documents():
    if "list_documents" in sys.modules:
        return sys.modules["list_documents"]
    return importlib.import_module("list_documents")


def test_list_documents_module_importable():
    mod = _import_list_documents()
    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "main")


def test_list_documents_parse_args_defaults():
    mod = _import_list_documents()
    args = mod.parse_args([])
    assert args.json is False


def test_list_documents_parse_args_json_flag():
    mod = _import_list_documents()
    args = mod.parse_args(["--json"])
    assert args.json is True


def test_list_documents_trunc_short():
    mod = _import_list_documents()
    assert mod._trunc("hello", 10) == "hello"


def test_list_documents_trunc_long():
    mod = _import_list_documents()
    result = mod._trunc("a" * 30, 10)
    assert len(result) == 10
    assert result.endswith("...")


def test_list_documents_trunc_none():
    mod = _import_list_documents()
    assert mod._trunc(None, 10) == "-"


# ---------------------------------------------------------------------------
# ask_document.py
# ---------------------------------------------------------------------------


def _import_ask_document():
    if "ask_document" in sys.modules:
        return sys.modules["ask_document"]
    return importlib.import_module("ask_document")


def test_ask_document_module_importable():
    mod = _import_ask_document()
    assert hasattr(mod, "parse_args")
    assert hasattr(mod, "main")


def test_ask_document_parse_args_positional():
    mod = _import_ask_document()
    args = mod.parse_args(["What is the maintenance interval?", "--latest"])
    assert args.question_positional == "What is the maintenance interval?"
    assert args.latest is True
    assert args.generate is False


def test_ask_document_parse_args_flag_question():
    mod = _import_ask_document()
    args = mod.parse_args(["--question", "How do I change the oil?", "--document", "Engine"])
    assert args.question == "How do I change the oil?"
    assert args.document == "Engine"


def test_ask_document_parse_args_generate():
    mod = _import_ask_document()
    args = mod.parse_args(["What is X?", "--latest", "--generate"])
    assert args.generate is True


def test_ask_document_parse_args_top_k():
    mod = _import_ask_document()
    args = mod.parse_args(["Q?", "--latest", "--top-k", "7"])
    assert args.top_k == 7


def test_ask_document_parse_args_show_context():
    mod = _import_ask_document()
    args = mod.parse_args(["Q?", "--latest", "--show-context"])
    assert args.show_context is True


def test_ask_document_parse_args_json():
    mod = _import_ask_document()
    args = mod.parse_args(["Q?", "--latest", "--json"])
    assert args.json is True


def test_ask_document_parse_args_document_id():
    mod = _import_ask_document()
    args = mod.parse_args(["Q?", "--document-id", "abc-123"])
    assert args.document_id == "abc-123"
    assert args.document is None
    assert args.latest is False


def test_ask_document_document_flags_mutually_exclusive():
    mod = _import_ask_document()
    with pytest.raises(SystemExit):
        mod.parse_args(["Q?", "--document-id", "abc", "--latest"])


def test_ask_document_resolve_question_positional():
    mod = _import_ask_document()
    args = mod.parse_args(["My question", "--latest"])
    assert mod.resolve_question(args) == "My question"


def test_ask_document_resolve_question_flag():
    mod = _import_ask_document()
    args = mod.parse_args(["--question", "My question", "--latest"])
    assert mod.resolve_question(args) == "My question"


def test_ask_document_main_no_question_returns_1():
    mod = _import_ask_document()
    result = mod.main([])
    assert result == 1


def test_ask_document_page_range_with_pages():
    mod = _import_ask_document()
    source = MagicMock()
    source.page_start = 10
    source.page_end = 12
    assert mod._page_range(source) == "pages 10-12"


def test_ask_document_page_range_single_page():
    mod = _import_ask_document()
    source = MagicMock()
    source.page_start = 5
    source.page_end = 5
    assert mod._page_range(source) == "page 5"


def test_ask_document_page_range_no_page():
    mod = _import_ask_document()
    source = MagicMock()
    source.page_start = None
    assert mod._page_range(source) == ""
