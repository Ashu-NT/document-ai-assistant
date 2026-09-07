from types import SimpleNamespace

from src.application.workflows.parsing.normalizers.table_rows.docling_table_extractor import (
    DoclingTableExtractor,
)
from src.application.workflows.parsing.normalizers.table_rows.docling_table_markdown_renderer import (
    DoclingTableMarkdownRenderer,
)


class FakeSerializer:
    def __init__(self) -> None:
        self.items: list[object] = []

    def serialize(self, *, item: object) -> SimpleNamespace:
        self.items.append(item)
        return SimpleNamespace(text=f"| Value |\n|---|\n| {item.value} |")


class FakeTable:
    def __init__(self, value: str) -> None:
        self.value = value
        self.export_calls = 0

    def export_to_markdown(self, doc=None) -> str:
        del doc
        self.export_calls += 1
        return "legacy"


def test_renderer_reuses_serializer_and_preserves_each_table_output() -> None:
    serializer = FakeSerializer()
    renderer = DoclingTableMarkdownRenderer(serializer)
    extractor = DoclingTableExtractor()
    first = FakeTable("A")
    second = FakeTable("B")

    first_text = extractor.extract_markdown(first, renderer=renderer)
    second_text = extractor.extract_markdown(second, renderer=renderer)

    assert first_text == "| Value |\n|---|\n| A |"
    assert second_text == "| Value |\n|---|\n| B |"
    assert serializer.items == [first, second]
    assert first.export_calls == 0
    assert second.export_calls == 0


def test_extractor_retains_existing_export_path_without_renderer() -> None:
    table = FakeTable("A")

    text = DoclingTableExtractor().extract_markdown(table, doc=object())

    assert text == "legacy"
    assert table.export_calls == 1
