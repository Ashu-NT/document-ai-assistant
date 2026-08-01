"""Subprocess-side worker for running a Docling conversion under a hard,
OS-enforced timeout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from src.infrastructure.parsing.docling.docling_converter_factory import (
    build_docling_converter,
)

if TYPE_CHECKING:
    import multiprocessing


@dataclass
class ConversionOutcome:
    """Picklable bundle of everything ``DoclingParser.parse()`` needs.

    Extracted inside the subprocess, where the real (unpicklable)
    ``ConversionResult`` lives, so only plain/picklable pieces ever have to
    cross the process boundary.
    """

    document: Any
    title: str | None
    page_count: int | None
    metadata: dict[str, Any]


def run_conversion_in_subprocess(
    file_path: str,
    conversion_kwargs: dict[str, Any],
    enable_ocr_override: bool | None,
    result_queue: "multiprocessing.Queue[Any]",
    converter_factory: Callable[..., Any] = build_docling_converter,
) -> None:
    """Entry point executed inside the spawned subprocess.
    """
    # Imported here rather than at module scope to avoid a circular import:
    # docling_parser.py imports this module to launch the subprocess, and only
    # needs the two static extraction helpers below (they don't need `self`).
    from src.infrastructure.parsing.docling.docling_parser import DoclingParser

    try:
        converter = converter_factory(enable_ocr_override=enable_ocr_override)
        conversion_result = converter.convert(file_path, **conversion_kwargs)
        raw_document = getattr(conversion_result, "document", None)
        outcome = ConversionOutcome(
            document=raw_document,
            title=(
                DoclingParser._extract_title(raw_document, file_path)
                if raw_document is not None
                else None
            ),
            page_count=(
                DoclingParser._extract_page_count(conversion_result, raw_document)
                if raw_document is not None
                else None
            ),
            metadata=DoclingParser._extract_metadata(conversion_result),
        )
        result_queue.put(("ok", outcome))
    except BaseException as exc:  # noqa: BLE001 - must always report failure to the parent
        try:
            result_queue.put(("error", exc))
        except Exception:
            # The exception itself wasn't picklable (rare, e.g. some native
            # extension error types) - fall back to a plain RuntimeError so
            # the parent still learns *why*, even if not the exact type.
            result_queue.put(("error", RuntimeError(str(exc))))


__all__ = ["ConversionOutcome", "run_conversion_in_subprocess"]
