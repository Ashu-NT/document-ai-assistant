from enum import StrEnum


class RetrievalBenchmarkCandidateRole(StrEnum):
    ATOMIC_EVIDENCE = "atomic_evidence"
    CONTEXT_COMPANION = "context_companion"
    ASSET_COMPANION = "asset_companion"
    OVERVIEW_COMPANION = "overview_companion"
