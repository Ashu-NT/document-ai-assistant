import yaml

from src.config.paths import PROJECT_ROOT

_CHUNKING_PROFILES_DIR = PROJECT_ROOT / "src" / "config" / "chunking"


def resolve_max_configured_chunk_tokens() -> int | None:
    """The most generous `max_chunk_tokens` ceiling across every per-
    document-type chunking profile (src/config/chunking/*.yaml).

    This is deliberately NOT "the one true budget for this document" - which
    document type's profile actually governed a given chunk depends on
    classification, which this evaluator does not run (see
    IngestionExpectationEvaluator's docstring). Using the max across every
    profile as a hard ceiling still catches catastrophic regressions (a
    chunk thousands of tokens long) without pretending to know a specific
    document's own tighter budget. Returns None if no profile can be read at
    all, so callers can skip the check rather than assert against a made-up
    number.
    """
    max_tokens: int | None = None
    if not _CHUNKING_PROFILES_DIR.is_dir():
        return None

    for profile_path in sorted(_CHUNKING_PROFILES_DIR.glob("*.yaml")):
        try:
            payload = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        value = payload.get("max_chunk_tokens") if isinstance(payload, dict) else None
        if isinstance(value, int):
            max_tokens = value if max_tokens is None else max(max_tokens, value)

    return max_tokens


__all__ = ["resolve_max_configured_chunk_tokens"]
