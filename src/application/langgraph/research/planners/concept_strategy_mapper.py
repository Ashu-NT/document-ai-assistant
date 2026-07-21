from __future__ import annotations

import re

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)
from src.application.langgraph.strategy_advisor.models.advisor_models import (
    StrategyAdvisorProposal,
)

CATEGORY_PATTERNS: tuple[tuple[re.Pattern[str], RetrievalStrategy], ...] = (
    (
        re.compile(
            r"\b(?:part\s*number|part\s*no\.?|p/?n\.?|serial\s*number|serial\s*no\.?|s/?n\.?|model\s*number|model\s*no\.?|drawing\s*number|drawing\s*no\.?|component\s*code|identifier|[A-Z]{2,3}-\d{3,})\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.IDENTIFIER_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:troubleshoot|troubleshooting|fault|error|alarm|failure|symptom|cause|remedy|recovery)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:maintenance|preventive maintenance|service|servicing|inspection|interval|schedule|lubrication|lubricate)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.MAINTENANCE_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:procedure|procedures|startup|start up|shutdown|shut down|commissioning|commission|operation|operate|install|installation|remove|replacement|replace)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.PROCEDURE_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:specification|specifications|technical data|technical|pressure|temperature|voltage|power|capacity|rating|dimension|dimensions|material|operating limit|limits)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.TECHNICAL_SPECIFICATION,
    ),
    (
        re.compile(
            r"\b(?:certificate|certification|approval|compliance|atex|iecex|surveyor)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.CERTIFICATION_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:drawing|diagram|schematic|layout|title block)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.DRAWING_LOOKUP,
    ),
    (
        re.compile(r"\b(?:figure|image|picture)\b", re.IGNORECASE),
        RetrievalStrategy.FIGURE_LOOKUP,
    ),
    (
        re.compile(
            r"\b(?:table|tables|matrix|list|lists|rows|columns|ordering example)\b",
            re.IGNORECASE,
        ),
        RetrievalStrategy.TABLE_LOOKUP,
    ),
)
_TABLE_HINT_RE = re.compile(
    r"\b(?:table|tables|schedule|matrix|rows|columns|specification table|ordering example|comparison table)\b",
    re.IGNORECASE,
)


def strategy_for_concept(concept: str) -> RetrievalStrategy:
    for pattern, strategy in CATEGORY_PATTERNS:
        if pattern.search(concept):
            return strategy
    return RetrievalStrategy.GENERAL_HYBRID


def requires_table(
    concepts: list[str],
    advisor_proposal: StrategyAdvisorProposal | None,
) -> bool:
    if advisor_proposal is not None and advisor_proposal.requires_table:
        return True
    return any(_TABLE_HINT_RE.search(concept) for concept in concepts)
