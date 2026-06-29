from src.application.workflows.question_answering.question_answering_route import (
    QuestionAnsweringRoute,
)
from src.application.workflows.retrieval.retrieval_query_analyzer import (
    RetrievalQueryAnalyzer,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.common import new_id
from src.domain.retrieval import RetrievalQuery


class QuestionAnsweringRouter:
    """Converts a raw question into a route decision and an analyzed RetrievalQuery.

    Using RetrievalQueryAnalyzer (not the bare IntentInferer) ensures identifier
    extraction and query rewriting happen once here so the resulting analyzed_query
    can be handed directly to RetrievalWorkflow without duplicate analysis.
    """

    def __init__(
        self,
        query_analyzer: RetrievalQueryAnalyzer | None = None,
    ) -> None:
        self._query_analyzer = query_analyzer or RetrievalQueryAnalyzer()

    def decide(
        self,
        question: str,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> tuple[QuestionAnsweringRoute, RetrievalQuery, RetrievalQueryIntent]:
        """Return the route and the fully-analyzed RetrievalQuery in one call.

        DOCUMENT_EXPLORATION is checked first; all other intents fall through to
        RETRIEVAL_QA so exploration is always a first-class branch.
        """
        raw_query = RetrievalQuery(
            query_id=new_id("q"),
            query_text=question,
            top_k=top_k,
            document_id=document_id,
        )
        analyzed = self._query_analyzer.analyze(raw_query)
        intent = self._query_analyzer.intent_inferer.infer(analyzed)

        if intent == RetrievalQueryIntent.DOCUMENT_EXPLORATION:
            return QuestionAnsweringRoute.DOCUMENT_EXPLORATION, analyzed, intent

        return QuestionAnsweringRoute.RETRIEVAL_QA, analyzed, intent
