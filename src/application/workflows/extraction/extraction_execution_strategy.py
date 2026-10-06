from enum import StrEnum


class ExtractionExecutionStrategy(StrEnum):
    """How ExtractionWorkflow turns one batch's requested entity families
    into LLM call(s).

    - MULTI_FAMILY (default, current production behavior, UNCHANGED by
      this enum's introduction): one call per batch, requesting the union
      of all candidate-narrowed families together (or every family, via
      FullExtractionPromptBuilder, when narrowing is disabled or resolves
      to everything).
    - SPECIALIZED_FAMILY (experimental): one call per (batch, family) pair,
      each using that family's own modular prompt builder
      (EXTRACTION_PROMPT_REGISTRY) instead of the combined/narrowed prompt.
      Tests the hypothesis that decomposing a multi-family workload into
      single-family calls improves small-model extraction quality - see
      outputs/evaluation/extraction/ for the controlled-experiment report.
    """

    MULTI_FAMILY = "multi_family"
    SPECIALIZED_FAMILY = "specialized_family"
