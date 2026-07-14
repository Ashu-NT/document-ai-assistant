from src.application.workflows.parsing.canonical_element import (
    CanonicalElement as ParsedCanonicalElement,
)
from src.application.workflows.parsing.builders.document_graph.source_location_factory import (
    SourceLocationFactory,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.domain.assets import AssetMetadata, PictureAsset, TableAsset, TableCellSpan
from src.domain.assets.table_rows.table_row_patterns import (
    drop_globally_empty_columns,
)
from src.shared.ids import IdGenerator


class ParsedAssetFactory:
    def __init__(self, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def build_table_asset(
        self,
        *,
        document_id: str,
        parent_section_id: str | None,
        parsed_element: ParsedCanonicalElement,
    ) -> tuple[str, TableAsset]:
        table_id = self.id_generator.new_id("table")
        return (
            table_id,
            TableAsset(
                table_id=table_id,
                document_id=document_id,
                markdown=(
                    self._clean_multiline_text(
                        parsed_element.metadata.get("markdown")
                        or parsed_element.text
                    )
                    or ""
                ),
                parent_section_id=parent_section_id,
                rows=self._clean_rows(parsed_element.metadata.get("table_rows")),
                row_ids=self._build_row_ids(
                    table_id=table_id,
                    row_count=(
                        parsed_element.metadata.get("row_count")
                        or len(parsed_element.metadata.get("table_rows") or [])
                    ),
                ),
                cell_spans=TableCellSpan.list_from_data(
                    parsed_element.metadata.get("table_cell_spans")
                ),
                row_count=parsed_element.metadata.get("row_count"),
                column_count=parsed_element.metadata.get("column_count"),
                table_shape=self._clean_text(parsed_element.metadata.get("table_shape")),
                metadata=AssetMetadata(
                    source=SourceLocationFactory.from_parsed(parsed_element),
                    caption=parsed_element.metadata.get("caption"),
                ),
            ),
        )

    def build_picture_asset(
        self,
        *,
        document_id: str,
        parent_section_id: str | None,
        parsed_element: ParsedCanonicalElement,
    ) -> tuple[str, PictureAsset]:
        picture_id = self.id_generator.new_id("picture")
        return (
            picture_id,
            PictureAsset(
                picture_id=picture_id,
                document_id=document_id,
                parent_section_id=parent_section_id,
                image_path=parsed_element.metadata.get("image_path"),
                ocr_text=parsed_element.metadata.get("ocr_text"),
                ocr_confidence=self._coerce_float(
                    parsed_element.metadata.get("ocr_confidence")
                ),
                ocr_provider=self._clean_text(
                    parsed_element.metadata.get("ocr_provider")
                ),
                ocr_mode=self._clean_text(
                    parsed_element.metadata.get("ocr_mode")
                    or parsed_element.metadata.get("ocr_target_type")
                ),
                metadata=AssetMetadata(
                    source=SourceLocationFactory.from_parsed(parsed_element),
                    caption=parsed_element.metadata.get("caption")
                    or parsed_element.text,
                ),
            ),
        )

    @staticmethod
    def _build_row_ids(*, table_id: str, row_count: object) -> list[str]:
        try:
            count = max(0, int(row_count))
        except (TypeError, ValueError):
            return []
        return [f"{table_id}:row:{index}" for index in range(count)]

    @staticmethod
    def _coerce_float(value: object) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _clean_text(value: object) -> str | None:
        text = repair_docling_text(str(value or "")).strip()
        return text or None

    @classmethod
    def _clean_multiline_text(cls, value: object) -> str | None:
        if value is None:
            return None
        lines = [
            repair_docling_text(str(line)).rstrip()
            for line in str(value).splitlines()
        ]
        text = "\n".join(lines).strip()
        return text or None

    @classmethod
    def _clean_rows(cls, rows: object) -> list[list[str]]:
        if not isinstance(rows, list):
            return []
        cleaned_rows: list[list[str]] = []
        for row in rows:
            if not isinstance(row, list):
                continue
            cleaned_rows.append(
                [
                    cls._clean_text(cell) or ""
                    for cell in row
                ]
            )
        return drop_globally_empty_columns(cleaned_rows)
