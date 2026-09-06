from __future__ import annotations


def render_structured_family_timing_console_lines(
    summary: dict[str, object],
) -> list[str]:
    families = summary.get("families")
    if not isinstance(families, list) or not families:
        return [
            "[graph] Structured family timing breakdown unavailable; "
            "no family stage metrics were recorded."
        ]

    total_seconds = _number(summary.get("select_specs_elapsed_seconds"))
    lines = [
        "[graph] Structured family timing breakdown "
        f"(select_specs={total_seconds:.3f}s):"
    ]
    for family in families:
        if not isinstance(family, dict):
            continue
        lines.append(
            "[graph]   "
            f"{str(family.get('family_builder', 'unknown')):<50} "
            f"{_number(family.get('elapsed_seconds')):>9.3f}s  "
            f"calls={int(_number(family.get('invocations'))):<6} "
            f"avg={_number(family.get('average_milliseconds')):>8.3f}ms  "
            f"specs={int(_number(family.get('specs'))):<6} "
            f"share={_number(family.get('select_specs_percent')):>6.2f}%"
        )
    return lines


def _number(value: object) -> float:
    if isinstance(value, bool):
        return float(value)
    return float(value) if isinstance(value, (int, float)) else 0.0
