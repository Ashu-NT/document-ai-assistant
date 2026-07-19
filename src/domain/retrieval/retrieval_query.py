from dataclasses import dataclass, field

from src.domain.common import ChunkType, DocumentType


@dataclass(slots=True)
class RetrievalQuery:
    query_id: str
    query_text: str

    document_types: list[DocumentType] = field(default_factory=list)
    chunk_types: list[ChunkType] = field(default_factory=list)

    detected_identifiers: list[str] = field(default_factory=list)

    document_id: str | None = None

    top_k: int = 5
    use_dense: bool = True
    use_keyword: bool = True
    use_sql: bool = True

    rewritten_query: str | None = None

    analyzed: bool = False

    # Plain string, not the RetrievalQueryIntent enum -- that enum is
    # application-layer, and this domain module must not import from
    # src.application (mirrors the RetrievedChunk.retrieval_source
    # precedent: an application-owned vocabulary stored as a bare string on
    # the domain object). Set by RetrievalQueryAnalyzer.analyze() so callers
    # that already have an analyzed query can skip re-running intent
    # inference; see RetrievalQueryIntentInferer.resolve().
    detected_intent: str | None = None

    # The classification behind detected_intent, previously computed and
    # then discarded the moment RetrievalQueryAnalyzer.analyze() returned --
    # persisted here so a later consumer (reflection's ambiguity check) can
    # read the SAME classification that actually drove retrieval instead of
    # re-running RetrievalQueryIntentInferer.classify() a second,
    # independent time (see answering_flow_weakness_remediation_plan.md,
    # PR 1-3). All optional/None until analyze() has run. intent_runner_up
    # is a plain string for the same domain/application-boundary reason as
    # detected_intent above.
    intent_best_score: int | None = None
    intent_runner_up_score: int | None = None
    intent_score_gap: int | None = None
    intent_confidence: float | None = None
    intent_runner_up: str | None = None

    def effective_query(self) -> str:
        return self.rewritten_query or self.query_text

    def has_identifiers(self) -> bool:
        return bool(self.detected_identifiers)