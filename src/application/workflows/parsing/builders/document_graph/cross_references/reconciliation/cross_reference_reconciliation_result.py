from dataclasses import dataclass, field

from src.domain.document.entities import ChunkCrossReference, CrossReferenceEvidence


@dataclass(slots=True, frozen=True)
class CrossReferenceReconciliationDiagnostics:
    single_source_count: int = 0
    confirmed_count: int = 0
    accepted_textual_count: int = 0
    accepted_native_count: int = 0
    conflict_count: int = 0
    unreconciled_multi_candidate_chunks: int = 0


@dataclass(slots=True, frozen=True)
class CrossReferenceReconciliationResult:
    evidence: list[CrossReferenceEvidence] = field(default_factory=list)
    canonical_references: list[ChunkCrossReference] = field(default_factory=list)
    diagnostics: CrossReferenceReconciliationDiagnostics = field(
        default_factory=CrossReferenceReconciliationDiagnostics
    )


__all__ = [
    "CrossReferenceReconciliationDiagnostics",
    "CrossReferenceReconciliationResult",
]
