from src.application.langgraph.retrieval_strategy.models import RetrievalContext
from src.application.langgraph.retrieval_strategy.services import RetrievalSignalExtractor
from src.domain.common import new_id
from src.domain.retrieval import RetrievalQuery


def test_retrieval_signal_extractor_detects_identifier_and_specification_signals() -> None:
    extractor = RetrievalSignalExtractor()
    context = RetrievalContext(
        query_text="Find part number HAM2423501 and test pressure",
        analyzed_query=RetrievalQuery(
            query_id=new_id("q"),
            query_text="Find part number HAM2423501 and test pressure",
            detected_identifiers=["ham2423501"],
        ),
    )

    signals = extractor.extract(context)

    assert any(signal.category == "identifier" for signal in signals)
    assert any(signal.category == "specification" for signal in signals)


def test_retrieval_signal_extractor_detects_maintenance_procedure_table_and_troubleshooting() -> None:
    extractor = RetrievalSignalExtractor()
    context = RetrievalContext(
        query_text=(
            "Show the maintenance schedule table and troubleshooting steps "
            "for replacing the filter"
        ),
    )

    signals = extractor.extract(context)
    categories = {signal.category for signal in signals}

    assert "maintenance" in categories
    assert "procedure" in categories
    assert "table" in categories
    assert "troubleshooting" in categories


def test_retrieval_signal_extractor_detects_certification_and_drawing_signals() -> None:
    extractor = RetrievalSignalExtractor()
    context = RetrievalContext(
        query_text="Find the certificate approval on the drawing figure layout",
        route="answer_question",
    )

    signals = extractor.extract(context)
    categories = {signal.category for signal in signals}

    assert "certification" in categories
    assert "drawing" in categories or "figure" in categories
