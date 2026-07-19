from src.application.workflows.retrieval import RetrievalQueryAnalyzer
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery


def test_retrieval_query_analyzer_extracts_identifiers_and_chunk_preferences() -> None:
    analyzer = RetrievalQueryAnalyzer()
    query = RetrievalQuery(
        query_id="query_001",
        query_text="What does ordering code MK311007 mean?",
    )

    analyzed = analyzer.analyze(query)

    assert analyzed.detected_identifiers == ["mk311007"]
    assert ChunkType.TECHNICAL_SPECIFICATION in analyzed.chunk_types
    assert ChunkType.SPARE_PARTS_TABLE in analyzed.chunk_types


def test_retrieval_query_analyzer_prefers_procedural_chunk_types() -> None:
    analyzer = RetrievalQueryAnalyzer()
    query = RetrievalQuery(
        query_id="query_002",
        query_text="How do I start and run the macerator?",
    )

    analyzed = analyzer.analyze(query)

    assert analyzed.detected_identifiers == []
    assert analyzed.chunk_types[:2] == [
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.MAINTENANCE_PROCEDURE,
    ]


def test_retrieval_query_analyzer_rewrites_common_identifier_abbreviations() -> None:
    analyzer = RetrievalQueryAnalyzer()
    query = RetrievalQuery(
        query_id="query_003",
        query_text="What is spare part no. P33?",
    )

    analyzed = analyzer.analyze(query)

    assert analyzed.rewritten_query == "What is spare part number P33?"


def test_retrieval_query_analyzer_prefers_overview_for_conceptual_system_question() -> None:
    analyzer = RetrievalQueryAnalyzer()
    query = RetrievalQuery(
        query_id="query_004",
        query_text="What does the FWC system do?",
    )

    analyzed = analyzer.analyze(query)

    assert analyzed.detected_identifiers == []
    assert analyzed.chunk_types[:2] == [
        ChunkType.OVERVIEW,
        ChunkType.GENERAL,
    ]


def test_retrieval_query_analyzer_widens_chunk_types_on_an_unresolved_intent_tie() -> None:
    # "table" and "fault" markers tie TABLE and TROUBLESHOOTING at an equal
    # score -- narrowing chunk_types to only the (arbitrarily
    # priority-ranked) winner would hard-exclude the tied alternative's
    # chunk types from both the dense and SQL candidate pools.
    analyzer = RetrievalQueryAnalyzer()
    query = RetrievalQuery(
        query_id="query_006",
        query_text="Show me the fault code table",
    )

    analyzed = analyzer.analyze(query)

    assert analyzed.detected_intent == "table"
    assert ChunkType.SPARE_PARTS_TABLE in analyzed.chunk_types
    assert ChunkType.TROUBLESHOOTING in analyzed.chunk_types


def test_retrieval_query_analyzer_persists_classification_scores_on_a_tie() -> None:
    """PR 1 (answering_flow_weakness_remediation_plan.md): the classification
    behind detected_intent used to be discarded the moment analyze()
    returned. It must now survive on the query object -- reusing the exact
    scenario from the tie test above, which independently confirms this is
    a genuine gap==0 tie, not a guessed fixture."""
    analyzer = RetrievalQueryAnalyzer()
    query = RetrievalQuery(
        query_id="query_007",
        query_text="Show me the fault code table",
    )

    analyzed = analyzer.analyze(query)

    assert analyzed.intent_best_score is not None
    assert analyzed.intent_runner_up_score is not None
    assert analyzed.intent_best_score == analyzed.intent_runner_up_score
    assert analyzed.intent_score_gap == 0
    assert analyzed.intent_runner_up == "troubleshooting"
    assert analyzed.intent_confidence is not None


def test_retrieval_query_analyzer_persists_a_clear_winners_score_and_gap() -> None:
    analyzer = RetrievalQueryAnalyzer()
    query = RetrievalQuery(
        query_id="query_008",
        query_text="How do I start and run the macerator?",
    )

    analyzed = analyzer.analyze(query)

    assert analyzed.intent_best_score is not None
    assert analyzed.intent_score_gap is not None
    assert analyzed.intent_score_gap > 0


def test_retrieval_query_analyzer_does_not_force_identifier_for_commissioning_objective() -> None:
    analyzer = RetrievalQueryAnalyzer()
    query = RetrievalQuery(
        query_id="query_005",
        query_text="What is the objective of commissioning the FWC12?",
    )

    analyzed = analyzer.analyze(query)

    assert "fwc12" in analyzed.detected_identifiers
    assert analyzed.chunk_types[:3] == [
        ChunkType.INSTALLATION_INSTRUCTION,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.MAINTENANCE_PROCEDURE,
    ]
