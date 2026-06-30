from src.application.langgraph.research.services.research_context_builder import (
    ResearchContextBuilder,
)
from src.application.langgraph.research.services.research_evidence_merger import (
    ResearchEvidenceMerger,
)
from src.application.langgraph.research.services.research_json_parser import (
    ResearchJsonParser,
)
from src.application.langgraph.research.services.research_state_mapper import (
    ResearchStateMapper,
)

__all__ = [
    "ResearchContextBuilder",
    "ResearchEvidenceMerger",
    "ResearchJsonParser",
    "ResearchStateMapper",
    "ResearchService",
]


def __getattr__(name: str):
    if name == "ResearchService":
        from src.application.langgraph.research.services.research_service import (
            ResearchService,
        )

        return ResearchService
    raise AttributeError(name)
