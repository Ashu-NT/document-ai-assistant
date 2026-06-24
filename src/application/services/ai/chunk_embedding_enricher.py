from src.domain.common import ChunkType

ENRICHED_CHUNK_TYPES: frozenset[ChunkType] = frozenset(
    {ChunkType.MAINTENANCE_INTERVAL, ChunkType.TECHNICAL_SPECIFICATION}
)


def maintenance_spec_aliases(*, content: str, section_path: list[str]) -> str | None:
    combined = " ".join([content] + section_path).lower()
    aliases: list[str] = []

    if any(k in combined for k in ("lubricat", "grease", "grease nipple", "shaft seal")):
        aliases.extend(
            ["lubrication interval", "greasing", "shaft seal lubrication", "grease schedule"]
        )

    if any(k in combined for k in ("oil quantit", "oil capacity", "oil volume", "oil fill", "fluid capacity")):
        aliases.extend(
            ["oil quantity", "oil specification", "fluid capacity", "oil fill quantity"]
        )

    if any(k in combined for k in ("oil change", "change interval", "replace oil", "renew oil", "drain screw")):
        aliases.extend(
            ["oil change interval", "oil replacement", "change frequency", "service interval"]
        )

    if any(k in combined for k in ("hours of operation", "every", "operating hours", "maintenance schedule", "lubrication schedule")):
        aliases.extend(
            ["maintenance interval", "service frequency", "operating hours", "scheduled maintenance"]
        )

    seen: set[str] = set()
    unique: list[str] = []
    for alias in aliases:
        if alias not in seen:
            seen.add(alias)
            unique.append(alias)
    return ", ".join(unique) if unique else None


def enrich_embedding_text(
    *,
    base_text: str,
    chunk_type: ChunkType,
    section_path: list[str],
    content: str,
) -> str:
    if chunk_type not in ENRICHED_CHUNK_TYPES:
        return base_text

    if "Related terms:" in base_text:
        return base_text

    additions: list[str] = []

    if section_path:
        local_title = section_path[-1]
        if f"Section: {local_title}" not in base_text:
            additions.append(f"Section: {local_title}")
        if len(section_path) >= 2:
            component = section_path[-2]
            if f"Component: {component}" not in base_text:
                additions.append(f"Component: {component}")

    aliases = maintenance_spec_aliases(content=content, section_path=section_path)
    if aliases:
        additions.append(f"Related terms: {aliases}")

    if not additions:
        return base_text

    return base_text + "\n\n" + "\n\n".join(additions)
