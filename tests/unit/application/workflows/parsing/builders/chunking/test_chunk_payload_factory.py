import pytest

from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
    _maintenance_spec_aliases,
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


class TestEmbeddingTextIncludesSectionPath:
    def test_section_path_present_for_all_chunk_types(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="Oil must be replaced every 500 hours.",
            section_path=["7 Components", "7.3 Pump", "Maintenance"],
            section_title="Maintenance",
            chunk_type=ChunkType.GENERAL,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "7 Components > 7.3 Pump > Maintenance" in payload.embedding_text

    def test_section_title_explicit_for_maintenance_chunk(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="Grease shaft seals every 350 operating hours.",
            section_path=["7 Components", "7.3 Vacuum Pump", "Lubrication Schedule"],
            section_title="Lubrication Schedule",
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Section: Lubrication Schedule" in payload.embedding_text

    def test_component_name_explicit_for_maintenance_chunk(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="After every 350 hours of operation, grease the nipple.",
            section_path=["7 Components", "7.3 Vacuum / Transfer Pump", "Lubrication Schedule"],
            section_title="Lubrication Schedule",
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Component: 7.3 Vacuum / Transfer Pump" in payload.embedding_text

    def test_component_omitted_when_section_path_has_single_segment(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="Oil quantity: 1.5 L.",
            section_path=["Oil Quantities"],
            section_title="Oil Quantities",
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Component:" not in payload.embedding_text

    def test_no_enrichment_for_general_chunk_type(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="Refer to this manual for operating instructions.",
            section_path=["7 Components", "7.3 Vacuum Pump", "Overview"],
            section_title="Overview",
            chunk_type=ChunkType.GENERAL,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Section:" not in payload.embedding_text
        assert "Component:" not in payload.embedding_text
        assert "Related terms:" not in payload.embedding_text


class TestContentNotPolluted:
    def test_content_does_not_include_aliases(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="After every 350 hours of operation, grease nipple should be lubricated.",
            section_path=["7 Components", "7.3 Pump", "Lubrication Schedule"],
            section_title="Lubrication Schedule",
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Related terms:" not in payload.content
        assert "shaft seal lubrication" not in payload.content

    def test_content_does_not_include_component_or_section_prefix(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="Drain the oil before replacing.",
            section_path=["7 Components", "7.3 Pump", "Oil Change"],
            section_title="Oil Change",
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Component:" not in payload.content
        assert "Section:" not in payload.content


class TestEmbeddingTextIncludesAliases:
    def test_lubrication_aliases_added_for_grease_content(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="After every 350 hours of operation, grease nipple should be lubricated.",
            section_path=["7 Components", "7.3 Vacuum Pump", "Lubrication Schedule"],
            section_title="Lubrication Schedule",
            chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Related terms:" in payload.embedding_text
        assert "shaft seal lubrication" in payload.embedding_text

    def test_oil_quantity_aliases_added_for_oil_table_content(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="| Rotary Lobe Pump | Oil quantity horizontal | Change interval |",
            section_path=["7 Components", "7.3 Pump", "7.3.9.4 Oil Quantities & Specification"],
            section_title="7.3.9.4 Oil Quantities & Specification",
            chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Related terms:" in payload.embedding_text
        assert any(
            term in payload.embedding_text
            for term in ("oil quantity", "oil specification", "oil change interval")
        )

    def test_no_aliases_for_technical_spec_without_maintenance_signals(self) -> None:
        factory = ChunkPayloadFactory()
        fragment = _make_fragment(
            text="Operating temperature: -20 to 80°C. Supply voltage: 24 V DC.",
            section_path=["Technical Data"],
            section_title="Technical Data",
            chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        )
        payload = factory.build_payload(
            document_title="Manual",
            fragments=[fragment],
        )
        assert "Related terms:" not in payload.embedding_text


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
