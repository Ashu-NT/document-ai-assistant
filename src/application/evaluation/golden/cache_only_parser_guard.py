from typing import Any

from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument


class GoldenCorpusDoclingUnavailableError(Exception):
    """Raised when the fast-regression runner is running in cached-only mode
    (`allow_real_parsing=False`) and a document has no cached parsed
    artifact - so real Docling conversion would otherwise be required."""


class CacheOnlyParserGuard:
    """Wraps a real `ParserPort` so `ParsingWorkflow`'s existing
    cache-check-then-parse flow is exercised unchanged, but an actual
    `.parse()` call (meaning the artifact store had no cached hit) raises
    instead of running real Docling conversion.

    Deliberately does not change ParsingWorkflow or the artifact store at
    all - it only ever wraps the parser instance the caller already built.
    """

    def __init__(self, parser: Any) -> None:
        self._parser = parser
        self.parser_name = parser.parser_name
        self.parser_version = parser.parser_version

    def resolve_conversion_fingerprint(
        self,
        *,
        enable_ocr_override: bool | None = None,
    ) -> str:
        return self._parser.resolve_conversion_fingerprint(
            enable_ocr_override=enable_ocr_override
        )

    def parse(
        self,
        file_path: str,
        *,
        enable_ocr_override: bool | None = None,
    ) -> RawParsedDocument:
        raise GoldenCorpusDoclingUnavailableError(
            "Cached-only evaluation mode: no cached parsed artifact for "
            f"{file_path!r} and real Docling conversion is disabled."
        )


__all__ = ["CacheOnlyParserGuard", "GoldenCorpusDoclingUnavailableError"]
