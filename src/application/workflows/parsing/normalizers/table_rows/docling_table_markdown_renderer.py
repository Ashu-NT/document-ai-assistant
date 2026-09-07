from typing import Any


class DoclingTableMarkdownRenderer:
    """Reuses one Docling serializer for every table in a document."""

    def __init__(self, serializer: Any) -> None:
        self.serializer = serializer

    @classmethod
    def try_create(cls, raw_document: Any) -> "DoclingTableMarkdownRenderer | None":
        try:
            from docling_core.transforms.serializer.markdown import (
                MarkdownDocSerializer,
            )
            from docling_core.types.doc import DoclingDocument
        except ImportError:
            return None

        if not isinstance(raw_document, DoclingDocument):
            return None
        return cls(MarkdownDocSerializer(doc=raw_document))

    def render(self, item: Any) -> str | None:
        result = self.serializer.serialize(item=item)
        text = getattr(result, "text", None)
        if text is None:
            return None
        cleaned = str(text).strip()
        return cleaned or None
