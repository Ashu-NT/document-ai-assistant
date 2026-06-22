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
