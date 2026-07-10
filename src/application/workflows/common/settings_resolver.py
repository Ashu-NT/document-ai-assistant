from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

# "Read a config setting, falling back to a hard-coded default if the
# config module can't be imported or the lookup otherwise fails" --
# previously reimplemented as ~13 near-identical `_default_*` functions
# across extraction_workflow.py, post_classification_chunk_finalization_
# workflow.py, and hybrid_document_type_resolver.py, each wrapping its own
# `try: from src.config.settings import ...; return ...\nexcept Exception:
# return <default>` boilerplate. Consolidated here as the single shared
# primitive; callers keep their own `_default_*() -> T` function per
# setting (for readability at the call site) but each one now just wraps
# its config lookup in a `loader` closure and delegates here.

T = TypeVar("T")


def resolve_setting(loader: Callable[[], T], default: T) -> T:
    try:
        return loader()
    except Exception:
        return default
