from src.application.evaluation.retrieval.benchmarking.resolution.models import (
    RetrievalBenchmarkCandidateRole,
)

_OVERVIEW_PREFIXES = ("section overview:",)
_CONTEXT_PREFIXES = ("context:",)
_ASSET_PREFIXES = ("figure:", "ocr:")
_ORDERED_PREFIXES = (
    *_OVERVIEW_PREFIXES,
    *_CONTEXT_PREFIXES,
    *_ASSET_PREFIXES,
)


def detect_candidate_role(content: str | None) -> RetrievalBenchmarkCandidateRole:
    first_line = _first_non_empty_line(content)
    if not first_line:
        return RetrievalBenchmarkCandidateRole.ATOMIC_EVIDENCE

    normalized = first_line.lower()
    if normalized.startswith(_OVERVIEW_PREFIXES):
        return RetrievalBenchmarkCandidateRole.OVERVIEW_COMPANION
    if normalized.startswith(_CONTEXT_PREFIXES):
        return RetrievalBenchmarkCandidateRole.CONTEXT_COMPANION
    if normalized.startswith(_ASSET_PREFIXES):
        return RetrievalBenchmarkCandidateRole.ASSET_COMPANION
    return RetrievalBenchmarkCandidateRole.ATOMIC_EVIDENCE


def strip_scaffolding_prefixes(content: str | None) -> str:
    if not content:
        return ""

    cleaned_lines: list[str] = []
    for raw_line in str(content).splitlines():
        line = raw_line.strip()
        if not line:
            continue

        lowered = line.lower()
        for prefix in _ORDERED_PREFIXES:
            if lowered.startswith(prefix):
                line = line[len(prefix):].strip(" :-")
                lowered = line.lower()
                break

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def _first_non_empty_line(content: str | None) -> str:
    if not content:
        return ""

    for line in str(content).splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned
    return ""
