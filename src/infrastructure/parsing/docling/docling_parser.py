import threading
from concurrent.futures import TimeoutError as ConversionTimeoutError
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.infrastructure.parsing.docling.docling_converter_factory import (
    build_docling_converter,
)
from src.shared.exceptions import DocumentParsingError, DocumentParsingTimeoutError


class DoclingParser:
    def __init__(
        self,
        converter: Any | None = None,
        *,
        max_num_pages: int | None = None,
        max_file_size_bytes: int | None = None,
        timeout_seconds: float | None = None,
        parser_name: str = "docling",
        parser_version: str | None = None,
    ) -> None:
        self.converter = converter or self._build_default_converter()
        self.max_num_pages = max_num_pages
        self.max_file_size_bytes = max_file_size_bytes
        self.timeout_seconds = timeout_seconds
        self.parser_name = parser_name
        self.parser_version = parser_version or self._resolve_parser_version()

    def parse(
        self,
        file_path: str,
        *,
        enable_ocr_override: bool | None = None,
    ) -> RawParsedDocument:
        try:
            converter = (
                self.converter
                if enable_ocr_override is None
                else self._build_default_converter(enable_ocr_override=enable_ocr_override)
            )
            conversion_kwargs: dict[str, Any] = {"raises_on_error": True}
            if self.max_num_pages is not None:
                conversion_kwargs["max_num_pages"] = self.max_num_pages
            if self.max_file_size_bytes is not None:
                conversion_kwargs["max_file_size"] = self.max_file_size_bytes

            conversion_result = self._convert_with_timeout(
                converter,
                file_path,
                conversion_kwargs,
            )

            raw_document = getattr(conversion_result, "document", None)
            if raw_document is None:
                raise DocumentParsingError(
                    "Docling parser returned no document.",
                    details={"file_path": file_path},
                )

            return RawParsedDocument(
                file_path=file_path,
                title=self._extract_title(raw_document, file_path),
                page_count=self._extract_page_count(
                    conversion_result,
                    raw_document,
                ),
                raw_document=raw_document,
                parser_name=self.parser_name,
                parser_version=self.parser_version,
                metadata=self._extract_metadata(conversion_result),
            )
        except DocumentParsingError:
            raise
        except ConversionTimeoutError as exc:
            raise DocumentParsingTimeoutError(
                f"Docling conversion exceeded {self.timeout_seconds}s.",
                details={
                    "file_path": file_path,
                    "timeout_seconds": self.timeout_seconds,
                },
            ) from exc
        except Exception as exc:
            raise DocumentParsingError(
                "Failed to parse document with Docling.",
                details={"file_path": file_path},
            ) from exc

    def _convert_with_timeout(
        self,
        converter: Any,
        file_path: str,
        conversion_kwargs: dict[str, Any],
    ) -> Any:
        if self.timeout_seconds is None:
            return converter.convert(file_path, **conversion_kwargs)

        # A daemon thread (not ThreadPoolExecutor) is used deliberately: Docling's
        # convert() is not cancellable, so a hung call leaves an orphaned thread.
        # ThreadPoolExecutor registers an atexit hook that joins every worker
        # thread before the process can exit, which would hang shutdown on that
        # same orphaned call. A plain daemon thread is dropped by the interpreter
        # instead.
        outcome: dict[str, Any] = {}

        def _run() -> None:
            try:
                outcome["value"] = converter.convert(file_path, **conversion_kwargs)
            except BaseException as exc:  # re-raised on the calling thread below
                outcome["error"] = exc

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()
        worker.join(timeout=self.timeout_seconds)

        if worker.is_alive():
            raise ConversionTimeoutError(
                f"Docling conversion exceeded {self.timeout_seconds}s."
            )
        if "error" in outcome:
            raise outcome["error"]
        return outcome["value"]

    @staticmethod
    def _build_default_converter(*, enable_ocr_override: bool | None = None) -> Any:
        return build_docling_converter(enable_ocr_override=enable_ocr_override)

    @staticmethod
    def _resolve_parser_version() -> str | None:
        try:
            return version("docling")
        except PackageNotFoundError:
            return None

    @staticmethod
    def _extract_title(raw_document: Any, file_path: str) -> str | None:
        for attribute_name in ("title", "name"):
            value = getattr(raw_document, attribute_name, None)
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return file_path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]

    @staticmethod
    def _extract_page_count(
        conversion_result: Any,
        raw_document: Any,
    ) -> int | None:
        num_pages = getattr(raw_document, "num_pages", None)
        if callable(num_pages):
            try:
                return int(num_pages())
            except Exception:
                pass
        elif num_pages is not None:
            try:
                return int(num_pages)
            except (TypeError, ValueError):
                pass

        pages = getattr(conversion_result, "pages", None)
        if pages is not None:
            try:
                return len(pages)
            except TypeError:
                return None

        return None

    @staticmethod
    def _extract_metadata(conversion_result: Any) -> dict[str, Any]:
        metadata: dict[str, Any] = {}

        status = getattr(conversion_result, "status", None)
        if status is not None:
            metadata["status"] = getattr(status, "value", str(status))

        confidence = getattr(conversion_result, "confidence", None)
        if confidence is not None:
            metadata["confidence"] = confidence

        return metadata
