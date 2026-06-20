from importlib.metadata import PackageNotFoundError, version
from typing import Any

from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument
from src.infrastructure.parsing.docling.docling_converter_factory import (
    build_docling_converter,
)
from src.shared.exceptions import DocumentParsingError


def _default_max_num_pages() -> int:
    try:
        from src.config.settings import ingestion_settings

        return ingestion_settings.max_pdf_pages
    except Exception:
        return 2**31 - 1


def _default_max_file_size_bytes() -> int:
    try:
        from src.config.settings import ingestion_settings

        return ingestion_settings.max_file_size_mb * 1024 * 1024
    except Exception:
        return 2**63 - 1


class DoclingParser:
    def __init__(
        self,
        converter: Any | None = None,
        *,
        max_num_pages: int | None = None,
        max_file_size_bytes: int | None = None,
        parser_name: str = "docling",
        parser_version: str | None = None,
    ) -> None:
        self.converter = converter or self._build_default_converter()
        self.max_num_pages = (
            max_num_pages
            if max_num_pages is not None
            else _default_max_num_pages()
        )
        self.max_file_size_bytes = (
            max_file_size_bytes
            if max_file_size_bytes is not None
            else _default_max_file_size_bytes()
        )
        self.parser_name = parser_name
        self.parser_version = parser_version or self._resolve_parser_version()

    def parse(self, file_path: str) -> RawParsedDocument:
        try:
            conversion_result = self.converter.convert(
                file_path,
                raises_on_error=True,
                max_num_pages=self.max_num_pages,
                max_file_size=self.max_file_size_bytes,
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
        except Exception as exc:
            raise DocumentParsingError(
                "Failed to parse document with Docling.",
                details={"file_path": file_path},
            ) from exc

    @staticmethod
    def _build_default_converter() -> Any:
        return build_docling_converter()

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
