from src.domain.common import ChunkType


def build_maintenance_spec_terms(
    *,
    content: str,
    section_path: list[str],
) -> list[str]:
    combined = _combined_text(content=content, section_path=section_path)
    aliases: list[str] = []

    if _contains_any(combined, ("lubricat", "grease", "grease nipple", "shaft seal")):
        aliases.extend(
            [
                "lubrication interval",
                "greasing",
                "shaft seal lubrication",
                "grease schedule",
            ]
        )

    if _contains_any(
        combined,
        ("oil quantit", "oil capacity", "oil volume", "oil fill", "fluid capacity"),
    ):
        aliases.extend(
            [
                "oil quantity",
                "oil specification",
                "fluid capacity",
                "oil fill quantity",
            ]
        )

    if _contains_any(
        combined,
        ("oil change", "change interval", "replace oil", "renew oil", "drain screw"),
    ):
        aliases.extend(
            [
                "oil change interval",
                "oil replacement",
                "change frequency",
                "service interval",
            ]
        )

    if _contains_any(
        combined,
        (
            "hours of operation",
            "every",
            "operating hours",
            "maintenance schedule",
            "lubrication schedule",
            "maintenance interval",
            "service life",
        ),
    ):
        aliases.extend(
            [
                "maintenance interval",
                "service frequency",
                "operating hours",
                "scheduled maintenance",
            ]
        )

    return _unique_preserve_order(aliases)


def build_chunk_related_terms(
    *,
    content: str,
    section_path: list[str],
    chunk_type: ChunkType,
) -> list[str]:
    combined = _combined_text(content=content, section_path=section_path)
    aliases = build_maintenance_spec_terms(content=content, section_path=section_path)

    if chunk_type == ChunkType.MAINTENANCE_PROCEDURE:
        aliases.extend(["maintenance procedure", "service procedure"])
        if _contains_any(combined, ("remove", "removal", "dismantl", "disassembl")):
            aliases.extend(["remove", "disassemble"])
        if _contains_any(combined, ("replace", "replacement", "renew")):
            aliases.extend(["replace", "replacement"])
        if _contains_any(combined, ("install", "installation", "reinstall", "fit")):
            aliases.extend(["install", "reinstall"])
        if _contains_any(combined, ("inspect", "inspection", "check", "adjust")):
            aliases.extend(["inspect", "adjust"])

    if chunk_type == ChunkType.OPERATION_INSTRUCTION:
        aliases.extend(["operation procedure", "operating instruction"])
        if _contains_any(combined, ("start", "start up", "startup", "switch on", "turn on")):
            aliases.extend(["start up", "startup"])
        if _contains_any(combined, ("stop", "shut down", "shutdown", "switch off", "turn off")):
            aliases.extend(["shutdown", "stop"])

    if chunk_type == ChunkType.TROUBLESHOOTING:
        aliases.extend(["fault diagnosis", "troubleshooting", "corrective action"])
        if _contains_any(
            combined,
            ("fault", "alarm", "warning", "cause", "remedy", "corrective action"),
        ):
            aliases.extend(["fault", "cause", "remedy", "alarm"])

    if chunk_type == ChunkType.SAFETY_WARNING:
        aliases.extend(["safety warning", "caution", "hazard"])
        if _contains_any(combined, ("danger", "warning", "disconnect power", "lock out")):
            aliases.extend(["danger", "disconnect power", "lock out"])

    if chunk_type == ChunkType.INSTALLATION_INSTRUCTION:
        aliases.extend(["installation procedure", "mounting instruction"])
        if _contains_any(combined, ("electrical connection", "wiring", "terminal")):
            aliases.extend(["electrical connection", "wiring"])
        if _contains_any(combined, ("pneumatic connection", "hose", "pipe")):
            aliases.extend(["pneumatic connection", "pipe connection"])

    if chunk_type == ChunkType.SPARE_PARTS_TABLE:
        aliases.extend(["spare parts", "parts list", "component list", "part number", "order code"])

    if chunk_type == ChunkType.CERTIFICATION_INFO:
        aliases.extend(["certificate", "approval", "compliance"])

    return _unique_preserve_order(aliases)


def _combined_text(*, content: str, section_path: list[str]) -> str:
    return " ".join([content] + section_path).lower()


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
