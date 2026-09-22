from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CorpusCoverageSummary:
    expected: int
    available: int
    evaluated: int
    missing_aliases: tuple[str, ...] = ()
    hash_mismatch_aliases: tuple[str, ...] = ()


__all__ = ["CorpusCoverageSummary"]
