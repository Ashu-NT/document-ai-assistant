import pytest

from src.application.services.ai.chunk_embedding_enricher import (
    maintenance_spec_aliases as _maintenance_spec_aliases,
)

from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)

from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)

from src.domain.common import ChunkType

def _make_fragment(
    *,
    text: str,
    section_path: list[str],
    section_title: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
    page_start: int | None = 1,
) -> ChunkFragment:
    return ChunkFragment(
        text=text,
        chunk_type=chunk_type,
        standalone=False,
        order_index=0,
        section_id="sec_001",
        section_title=section_title,
        section_path=section_path,
        section_level=2,
        parent_section_id=None,
        element_ids=["el_001"],
        table_ids=[],
        picture_ids=[],
        page_start=page_start,
        page_end=page_start,
        token_count=len(text.split()),
    )

class TestMaintenanceSpecAliasHelper:
    def test_grease_content_triggers_lubrication_aliases(self) -> None:
        result = _maintenance_spec_aliases(
            content="After every 350 hours of operation, grease the nipple.",
            section_path=["7.3 Vacuum Pump", "Lubrication Schedule"],
        )
        assert result is not None
        assert "shaft seal lubrication" in result

    def test_oil_quantity_content_triggers_oil_aliases(self) -> None:
        result = _maintenance_spec_aliases(
            content="The housing requires the following oil quantity: 1.5 L horizontal.",
            section_path=["Oil Quantities & Specification"],
        )
        assert result is not None
        assert "oil quantity" in result or "oil specification" in result

    def test_change_interval_content_triggers_change_aliases(self) -> None:
        result = _maintenance_spec_aliases(
            content="Change interval: every 1000 hours.",
            section_path=["Maintenance"],
        )
        assert result is not None
        assert "oil change interval" in result or "service interval" in result

    def test_unrelated_content_returns_none(self) -> None:
        result = _maintenance_spec_aliases(
            content="Refer to the appendix for wiring diagrams.",
            section_path=["Electrical Connection"],
        )
        assert result is None

    def test_aliases_are_deduplicated(self) -> None:
        result = _maintenance_spec_aliases(
            content="After every 350 hours of operation grease the shaft seal. Change interval applies.",
            section_path=["Lubrication Schedule"],
        )
        assert result is not None
        terms = [t.strip() for t in result.split(",")]
        assert len(terms) == len(set(terms)), "Aliases must not contain duplicates"


class TestMergedChunkTouchedSectionIds:
    """Regression coverage for the section-path collapse bug: when
    SectionMergePolicy folds several sibling subsections into one chunk,
    ChunkPayloadFactory must still record every subsection it drew content
    from in `section_ids`, even though `section_id`/`section_path` stay the
    common ancestor for display."""

    def test_merged_sibling_sections_are_all_recorded_in_section_ids(self) -> None:
        factory = ChunkPayloadFactory()
        fragments = [
            _make_fragment(
                text="General provisions apply to this contract.",
                section_path=["1 General"],
                section_title="1 General",
            ),
            _make_fragment(
                text="1.7 Modifications require written consent.",
                section_path=["1 General", "1.7 Modifications"],
                section_title="1.7 Modifications",
            ),
            _make_fragment(
                text="1.8 Liability and Warranty is limited as described below.",
                section_path=["1 General", "1.8 Liability and Warranty"],
                section_title="1.8 Liability and Warranty",
            ),
        ]
        section_path_lookup = {
            ("1 General",): "sec_general",
            ("1 General", "1.7 Modifications"): "sec_17",
            ("1 General", "1.8 Liability and Warranty"): "sec_18",
        }

        payload = factory.build_payload(
            document_title="Manual",
            fragments=fragments,
            section_path_lookup=section_path_lookup,
        )

        assert payload.section_id == "sec_general"
        assert payload.section_path == ["1 General"]
        assert payload.section_ids == ["sec_general", "sec_17", "sec_18"]
        # The subsection headings that got merged away from section_path
        # must still be recoverable from the chunk's own content.
        assert "1.7 Modifications" in payload.content
        assert "1.8 Liability and Warranty" in payload.content

    def test_single_section_chunk_has_only_its_own_id_in_section_ids(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="Refer to this manual for operating instructions.",
            section_path=["Overview"],
            section_title="Overview",
        )
        section_path_lookup = {("Overview",): "sec_overview"}

        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
            section_path_lookup=section_path_lookup,
        )

        assert payload.section_ids == ["sec_overview"]

    def test_section_ids_falls_back_to_fragment_section_id_without_lookup(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="Refer to this manual for operating instructions.",
            section_path=["Overview"],
            section_title="Overview",
        )

        payload = factory.build_payload(document_title="Manual", fragments=[fragment])

        assert payload.section_ids == ["sec_001"]
