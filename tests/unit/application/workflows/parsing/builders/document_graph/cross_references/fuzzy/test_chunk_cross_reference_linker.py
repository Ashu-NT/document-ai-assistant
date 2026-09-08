from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_linker import (
    ChunkCrossReferenceLinker,
)
from src.domain.assets import TableAsset
from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.common import DocumentType, SourceLocation
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus, ChunkCrossReferenceType
from src.domain.document.entities.chunk import DocumentChunk
from src.domain.document.entities.document import Document
from src.domain.document.value_objects import DocumentHashes
from src.shared.ids import IdGenerator


def make_chunk(
    *,
    chunk_id: str,
    content: str,
    table_ids: list[str] | None = None,
    section_path: list[str] | None = None,
    sequence_number: int = 1,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        section_path=section_path or [],
        content=content,
        source=SourceLocation(page_start=1, page_end=1),
        table_ids=table_ids or [],
        sequence_number=sequence_number,
    )


def make_graph(chunks: list[DocumentChunk], tables: dict[str, TableAsset]) -> DocumentGraph:
    document = Document(
        document_id="doc_001",
        file_name="manual.pdf",
        file_path="data/input/manual.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
        document_type=DocumentType.MANUAL,
    )
    graph = DocumentGraph(document=document)
    for chunk in chunks:
        graph.add_chunk(chunk)
    graph.tables = tables
    return graph


def test_link_resolves_a_table_reference_to_the_chunk_containing_that_table() -> None:
    table = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption="Table 3. Spare parts list"),
    )
    referencing_chunk = make_chunk(
        chunk_id="ref", content="Spare parts are listed in Table 3."
    )
    target_chunk = make_chunk(
        chunk_id="target", content="table contents here", table_ids=["table_1"]
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={"table_1": table})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert len(cross_references) == 1
    xref = cross_references[0]
    assert xref.reference_type == ChunkCrossReferenceType.TABLE_REFERENCE
    assert xref.source_chunk_id == "ref"
    assert xref.target_chunk_id == "target"
    assert xref.target_asset_label == "3"
    assert xref.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE


def test_link_leaves_a_table_reference_unresolved_when_no_asset_is_captioned_with_that_number() -> (
    None
):
    referencing_chunk = make_chunk(chunk_id="ref", content="See Table 9 for details.")
    graph = make_graph([referencing_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert len(cross_references) == 1
    xref = cross_references[0]
    assert xref.reference_type == ChunkCrossReferenceType.TABLE_REFERENCE
    assert xref.target_chunk_id is None
    assert xref.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED


def test_link_falls_back_to_page_proximity_when_table_has_no_caption() -> None:
    table = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption=None),
    )
    referencing_chunk = make_chunk(
        chunk_id="ref", content="Spare parts are listed in Table 3."
    )
    target_chunk = make_chunk(
        chunk_id="target", content="table contents here", table_ids=["table_1"]
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={"table_1": table})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert len(cross_references) == 1
    xref = cross_references[0]
    assert xref.target_chunk_id == "target"
    assert xref.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    assert xref.confidence_score == 0.3


def test_link_does_not_self_reference_when_the_table_reference_lands_on_its_own_chunk() -> (
    None
):
    table = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption="Table 3. Spare parts list"),
    )
    # The chunk containing the table also happens to mention "Table 3" in
    # its own text (e.g. a caption echoed into the chunk content).
    chunk = make_chunk(
        chunk_id="self",
        content="Table 3. Spare parts list",
        table_ids=["table_1"],
    )
    graph = make_graph([chunk], tables={"table_1": table})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert cross_references == []


def test_link_resolves_an_explicit_section_reference_with_no_anchors_present() -> None:
    # Preserves today's accepted behavior for "see section"/"chap." -- an
    # explicit lead-in with no anchors either way still resolves, exactly
    # as it did before the qualifier was introduced.
    referencing_chunk = make_chunk(
        chunk_id="ref", content="See section 9 for wiring details.", sequence_number=1
    )
    target_chunk = make_chunk(
        chunk_id="target",
        content="Wiring details go here.",
        section_path=["9 Wiring"],
        sequence_number=2,
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    section_refs = [
        xref
        for xref in cross_references
        if xref.reference_type == ChunkCrossReferenceType.SECTION_REFERENCE
    ]
    assert len(section_refs) == 1
    assert section_refs[0].target_chunk_id == "target"
    assert section_refs[0].resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE


def test_link_resolves_an_alternate_phrasing_section_reference() -> None:
    # Regression for the redesign's core motivation: "with reference to
    # section" used to be invisible to the detector entirely.
    referencing_chunk = make_chunk(
        chunk_id="ref",
        content="With reference to section 9.4, item 13 above, refit the end shield.",
        sequence_number=1,
    )
    target_chunk = make_chunk(
        chunk_id="target",
        content="End shield refit instructions.",
        section_path=["9.4 End Shield"],
        sequence_number=2,
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    section_refs = [
        xref
        for xref in cross_references
        if xref.reference_type == ChunkCrossReferenceType.SECTION_REFERENCE
    ]
    assert len(section_refs) == 1
    assert section_refs[0].target_chunk_id == "target"
    assert section_refs[0].matched_text == "With reference to section 9.4"


def test_link_drops_a_generic_bare_section_mention_that_cites_an_external_directive() -> (
    None
):
    # The core behavior change: a bare "Section N" next to an external
    # standards-body anchor no longer produces a cross-reference at all --
    # not even an unresolved one -- because it never proceeds past
    # qualification.
    referencing_chunk = make_chunk(
        chunk_id="ref",
        content=(
            "The latest version of the Directive for Machinery, Annex I, "
            "Section 1.2 Controls should be observed."
        ),
        section_path=["1.2 Something Unrelated"],
    )
    graph = make_graph([referencing_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert cross_references == []


def test_link_drops_an_ambiguous_generic_bare_section_mention_with_no_signal_either_way() -> (
    None
):
    referencing_chunk = make_chunk(
        chunk_id="ref", content="Section 12.9 was updated last year."
    )
    graph = make_graph([referencing_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert cross_references == []


def test_link_resolves_a_generic_bare_section_mention_with_an_internal_anchor() -> None:
    referencing_chunk = make_chunk(
        chunk_id="ref",
        content="Section 4.2 of this manual covers installation drawings.",
        sequence_number=1,
    )
    target_chunk = make_chunk(
        chunk_id="target",
        content="Installation drawing details.",
        section_path=["4.2 Installation Drawings"],
        sequence_number=2,
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    section_refs = [
        xref
        for xref in cross_references
        if xref.reference_type == ChunkCrossReferenceType.SECTION_REFERENCE
    ]
    assert len(section_refs) == 1
    assert section_refs[0].target_chunk_id == "target"


def test_link_drops_an_explicit_lead_in_section_reference_when_the_target_is_missing() -> (
    None
):
    # Target-existence is now a required qualification condition, not just
    # a resolver-level fallback: an explicit lead-in pointing at a number
    # that doesn't exist anywhere in this document is withheld as
    # AMBIGUOUS before ever reaching the resolver -- no cross-reference
    # row is produced at all (not even an UNRESOLVED one). Since
    # qualification and resolution now check target-existence against the
    # same index, a qualified-INTERNAL section reference always resolves;
    # UNRESOLVED is no longer reachable through this path.
    referencing_chunk = make_chunk(
        chunk_id="ref", content="Refer to section 99.9 for details."
    )
    graph = make_graph([referencing_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert cross_references == []


def test_link_qualifies_a_mixed_internal_and_external_reference_in_the_same_chunk_independently() -> (
    None
):
    referencing_chunk = make_chunk(
        chunk_id="ref",
        content=(
            "Refer to section 5.2 for calibration steps. "
            "This procedure also mirrors the ISO 9001 standard for reference."
        ),
        section_path=["1 Intro"],
        sequence_number=1,
    )
    target_chunk = make_chunk(
        chunk_id="target",
        content="Calibration steps go here.",
        section_path=["5.2 Calibration"],
        sequence_number=2,
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    section_refs = [
        xref
        for xref in cross_references
        if xref.reference_type == ChunkCrossReferenceType.SECTION_REFERENCE
    ]
    assert len(section_refs) == 1
    assert section_refs[0].target_chunk_id == "target"
    assert section_refs[0].matched_text == "Refer to section 5.2"


def test_link_resolves_an_annex_reference_to_the_chunk_mentioning_that_label() -> None:
    # Real document shape: annex/appendix sub-numbering that never became
    # its own section heading, only ever appearing as plain chunk content.
    referencing_chunk = make_chunk(
        chunk_id="ref",
        content="Refer to Annex 2 for sensor locations.",
        sequence_number=1,
    )
    target_chunk = make_chunk(
        chunk_id="target",
        content="8.2 Annex 2\n\nSensors",
        sequence_number=2,
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    annex_refs = [
        xref
        for xref in cross_references
        if xref.reference_type == ChunkCrossReferenceType.ANNEX_REFERENCE
    ]
    assert len(annex_refs) == 1
    assert annex_refs[0].target_chunk_id == "target"
    assert annex_refs[0].target_annex_label == "2"
    assert annex_refs[0].resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE


def test_link_resolves_a_letter_appendix_reference() -> None:
    referencing_chunk = make_chunk(
        chunk_id="ref", content="See Appendix B for calibration data.", sequence_number=1
    )
    target_chunk = make_chunk(
        chunk_id="target", content="Appendix B: Calibration Data", sequence_number=2
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    annex_refs = [
        xref
        for xref in cross_references
        if xref.reference_type == ChunkCrossReferenceType.ANNEX_REFERENCE
    ]
    assert len(annex_refs) == 1
    assert annex_refs[0].target_chunk_id == "target"
    assert annex_refs[0].target_annex_label == "B"


def test_link_drops_a_bare_annex_mention_that_cites_an_external_directive() -> None:
    # Real document (corpus review): "Annex V regulations must be observed"
    # cites an external directive's own Annex V using the same bare
    # phrasing a genuine internal reference would use.
    referencing_chunk = make_chunk(
        chunk_id="ref",
        content="The latest Directive Annex V regulations must be observed.",
    )
    graph = make_graph([referencing_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert cross_references == []


def test_link_still_produces_no_annex_reference_when_no_chunk_mentions_the_label() -> (
    None
):
    referencing_chunk = make_chunk(
        chunk_id="ref", content="Refer to Annex 9 for details."
    )
    graph = make_graph([referencing_chunk], tables={})

    cross_references = ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    # Qualified INTERNAL (explicit lead-in, but no anchor and the label 9
    # doesn't exist anywhere -> AMBIGUOUS, same target-existence-required
    # rule as section references), so nothing is produced at all.
    assert cross_references == []


def test_link_logs_a_debug_summary_with_counts_by_reference_type(caplog) -> None:
    table = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| a | b |",
        metadata=AssetMetadata(caption="Table 3. Spare parts list"),
    )
    referencing_chunk = make_chunk(
        chunk_id="ref", content="Spare parts are listed in Table 3."
    )
    target_chunk = make_chunk(
        chunk_id="target", content="table contents here", table_ids=["table_1"]
    )
    graph = make_graph([referencing_chunk, target_chunk], tables={"table_1": table})
    logger_name = (
        "src.application.workflows.parsing.builders.document_graph"
        ".cross_references.fuzzy.chunk_cross_reference_linker"
    )

    with caplog.at_level("DEBUG", logger=logger_name):
        ChunkCrossReferenceLinker(id_generator=IdGenerator()).link(graph)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == 10  # DEBUG
    message = record.getMessage()
    assert "stage=fuzzy_cross_reference_linker" in message
    assert "status=ok" in message
    assert "document_id=doc_001" in message
    assert "table_reference=1" in message
    assert "total=1" in message
