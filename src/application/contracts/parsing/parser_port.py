from typing import Protocol

from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument


class ParserPort(Protocol):
    parser_name: str
    parser_version: str | None

    def parse(
        self,
        file_path: str,
        *,
        enable_ocr_override: bool | None = None,
    ) -> RawParsedDocument:
        ...
