from src.application.workflows.parsing.normalizers import DoclingDocumentNormalizer
from src.application.workflows.parsing.profiling import GraphBuildProfiler
from tests.unit.application.workflows.parsing.normalizers._test_docling_document_normalizer_part1 import (
    FakeDoclingItem,
    FakeProvenance,
    FakeRawDocument,
    make_raw_parsed_document,
)


def test_normalizer_reports_coarse_internal_stage_metrics() -> None:
    raw_document = FakeRawDocument(
        [
            FakeDoclingItem(
                label="text",
                text="Pump operating instructions.",
                self_ref="#/texts/1",
                prov=[FakeProvenance(1)],
            )
        ]
    )
    profiler = GraphBuildProfiler(enabled=True)

    elements = DoclingDocumentNormalizer(profiler=profiler).normalize(
        make_raw_parsed_document(raw_document),
        "doc_profile",
    )

    assert len(elements) == 1
    names = {metric.name for metric in profiler.stage_metrics}
    assert {
        "canonical_normalizer.collect_items",
        "canonical_normalizer.build_caption_index",
        "canonical_normalizer.analyze_layout",
        "canonical_normalizer.prepare_table_renderer",
        "canonical_normalizer.normalize_items",
        "canonical_normalizer.apply_reading_order",
        "canonical_normalizer.apply_text_grid_fallback",
    } <= names
