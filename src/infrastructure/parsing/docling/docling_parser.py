import multiprocessing
import queue
import time
from concurrent.futures import TimeoutError as ConversionTimeoutError
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Callable

from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.infrastructure.parsing.docling.docling_conversion_worker import (
    ConversionOutcome,
    run_conversion_in_subprocess,
)
from src.infrastructure.parsing.docling.docling_converter_factory import (
    build_docling_converter,
)
from src.shared.exceptions import DocumentParsingError, DocumentParsingTimeoutError

# How long to wait on the result queue after the subprocess has already
# exited (normally or via terminate/kill): the queue.put() happens-before the
# process exit in the success/error paths, so this is just a defensive bound
# against an unlikely OS-level scheduling race, not a real conversion budget.
_RESULT_QUEUE_DRAIN_TIMEOUT_SECONDS = 5.0

# Grace period given to a timed-out subprocess between SIGTERM and SIGKILL.
_TERMINATE_GRACE_PERIOD_SECONDS = 5.0


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
        converter_factory: Callable[..., Any] | None = None,
    ) -> None:
        
        self.timeout_seconds =timeout_seconds
        
        if converter is not None:
            self.converter = converter
        elif timeout_seconds is None:
            self.converter = self._build_default_converter()
        else:
            self.converter = None
            
        self.max_num_pages = max_num_pages
        self.max_file_size_bytes = max_file_size_bytes
        
        self.parser_name = parser_name
        self.parser_version = parser_version or self._resolve_parser_version()
        self._converter_factory = converter_factory or build_docling_converter

    def parse(
        self,
        file_path: str,
        *,
        enable_ocr_override: bool | None = None,
    ) -> RawParsedDocument:
        try:
            conversion_kwargs: dict[str, Any] = {"raises_on_error": True}
            if self.max_num_pages is not None:
                conversion_kwargs["max_num_pages"] = self.max_num_pages
            if self.max_file_size_bytes is not None:
                conversion_kwargs["max_file_size"] = self.max_file_size_bytes

            outcome = self._convert_with_timeout(
                file_path,
                conversion_kwargs,
                enable_ocr_override,
            )

            if outcome.document is None:
                raise DocumentParsingError(
                    "Docling parser returned no document.",
                    details={"file_path": file_path},
                )

            return RawParsedDocument(
                file_path=file_path,
                title=outcome.title,
                page_count=outcome.page_count,
                raw_document=outcome.document,
                parser_name=self.parser_name,
                parser_version=self.parser_version,
                metadata=outcome.metadata,
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
        file_path: str,
        conversion_kwargs: dict[str, Any],
        enable_ocr_override: bool | None,
    ) -> ConversionOutcome:
        if self.timeout_seconds is None:
            converter = (
                self.converter
                if enable_ocr_override is None
                else self._build_default_converter(
                    enable_ocr_override=enable_ocr_override
                )
            )
            conversion_result = converter.convert(file_path, **conversion_kwargs)
            raw_document = getattr(conversion_result, "document", None)
            return ConversionOutcome(
                document=raw_document,
                title=(
                    self._extract_title(raw_document, file_path)
                    if raw_document is not None
                    else None
                ),
                page_count=(
                    self._extract_page_count(conversion_result, raw_document)
                    if raw_document is not None
                    else None
                ),
                metadata=self._extract_metadata(conversion_result),
            )

        return self._convert_in_subprocess(
            file_path,
            conversion_kwargs,
            enable_ocr_override,
        )

    def _convert_in_subprocess(
        self,
        file_path: str,
        conversion_kwargs: dict[str, Any],
        enable_ocr_override: bool | None,
    ) -> ConversionOutcome:
        result_queue: multiprocessing.Queue = multiprocessing.Queue(maxsize=1)

        process = multiprocessing.Process(
            target=run_conversion_in_subprocess,
            args=(
                file_path,
                conversion_kwargs,
                enable_ocr_override,
                result_queue,
                self._converter_factory,
            ),
        )

        process.start()

        deadline = time.monotonic() + self.timeout_seconds

        try:
            while True:
                remaining = deadline - time.monotonic()

                if remaining <= 0:
                    self._terminate_process(process)

                    raise ConversionTimeoutError(
                        f"Docling conversion exceeded "
                        f"{self.timeout_seconds}s."
                    )

                try:
                    status, payload = result_queue.get(
                        timeout=min(0.5, remaining)
                    )
                    break

                except queue.Empty:
                    if process.is_alive():
                        continue

                    process.join()

                    if process.exitcode not in (0, None):
                        raise DocumentParsingError(
                            "Docling conversion subprocess exited unexpectedly "
                            f"(exit code {process.exitcode}).",
                            details={
                                "file_path": file_path,
                                "exitcode": process.exitcode,
                            },
                        )

                    # Defensive final drain in case process shutdown and queue
                    # availability crossed very closely.
                    try:
                        status, payload = result_queue.get(
                            timeout=_RESULT_QUEUE_DRAIN_TIMEOUT_SECONDS
                        )
                        break
                    except queue.Empty as exc:
                        raise DocumentParsingError(
                            "Docling conversion subprocess exited without "
                            "producing a result.",
                            details={"file_path": file_path},
                        ) from exc

            # The parent has now consumed the potentially large queue payload,
            # so the worker's queue feeder can finish and the process can exit.
            process.join(timeout=_TERMINATE_GRACE_PERIOD_SECONDS)

            if process.is_alive():
                self._terminate_process(process)

            if status == "error":
                raise payload

            return payload

        finally:
            if process.is_alive():
                self._terminate_process(process)

            result_queue.close()


    @staticmethod
    def _terminate_process(process: multiprocessing.Process) -> None:
        process.terminate()
        process.join(timeout=_TERMINATE_GRACE_PERIOD_SECONDS)

        if process.is_alive():
            process.kill()
            process.join()


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
