from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    resolve_parser_extra,
)
from src.application.workflows.parsing.parsing_value_coercion import (
    coerce_positive_int,
)
from src.domain.elements import CanonicalElement


class TableChunkEligibilityPolicy:
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
    ) -> None:
        self.text_splitter = text_splitter

    def should_chunk(
        self,
        element: CanonicalElement,
    ) -> bool:
        parser_extra = resolve_parser_extra(element)

        column_count = coerce_positive_int(
            parser_extra.get("column_count")
        )
        row_count = coerce_positive_int(
            parser_extra.get("row_count")
        )
        markdown = (
            clean_chunk_text(
                parser_extra.get("markdown") or element.text
            )
            or ""
        )

        if column_count is not None and column_count <= 1:
            return False

        if (
            row_count is not None
            and row_count <= 1
            and self.text_splitter.count_tokens(markdown) > 30
        ):
            return False

        return True