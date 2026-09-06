from __future__ import annotations

_SELECT_SPECS_STAGE = "structured_family_spec_factory.select_specs"
_FAMILY_STAGE_PREFIX = f"{_SELECT_SPECS_STAGE}."


def build_structured_family_timing_summary(
    stage_metrics: list[dict[str, object]],
) -> dict[str, object]:
    """Build a serializable timing summary from dynamic family stage metrics."""
    select_specs_seconds = 0.0
    families: list[dict[str, object]] = []

    for metric in stage_metrics:
        name = str(metric.get("name", ""))
        elapsed_seconds = _number(metric.get("elapsed_seconds"))
        if name == _SELECT_SPECS_STAGE:
            select_specs_seconds = elapsed_seconds
            continue
        if not name.startswith(_FAMILY_STAGE_PREFIX):
            continue

        operations = _mapping(metric.get("operations"))
        output_counts = _mapping(metric.get("output_counts"))
        invocations = int(_number(operations.get("invocations")))
        families.append(
            {
                "family_builder": name.removeprefix(_FAMILY_STAGE_PREFIX),
                "stage_name": name,
                "elapsed_seconds": elapsed_seconds,
                "invocations": invocations,
                "average_milliseconds": (
                    (elapsed_seconds * 1000.0) / invocations
                    if invocations > 0
                    else 0.0
                ),
                "specs": int(_number(output_counts.get("specs"))),
            }
        )

    families.sort(
        key=lambda family: float(family["elapsed_seconds"]),
        reverse=True,
    )
    family_seconds = sum(float(family["elapsed_seconds"]) for family in families)
    for family in families:
        family["select_specs_percent"] = (
            (float(family["elapsed_seconds"]) / select_specs_seconds) * 100.0
            if select_specs_seconds > 0
            else 0.0
        )

    return {
        "select_specs_elapsed_seconds": select_specs_seconds,
        "family_elapsed_seconds": family_seconds,
        "unattributed_elapsed_seconds": max(
            select_specs_seconds - family_seconds,
            0.0,
        ),
        "accounted_percent": (
            (family_seconds / select_specs_seconds) * 100.0
            if select_specs_seconds > 0
            else 0.0
        ),
        "families": families,
    }


def _mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _number(value: object) -> float:
    if isinstance(value, bool):
        return float(value)
    return float(value) if isinstance(value, (int, float)) else 0.0
