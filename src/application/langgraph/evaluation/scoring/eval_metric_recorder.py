from __future__ import annotations


def record_check(
    metric_name: str,
    passed: bool | None,
    metrics: dict[str, float],
    failed_checks: list[str],
) -> None:
    if passed is None:
        return
    metrics[metric_name] = 1.0 if passed else 0.0
    if not passed:
        failed_checks.append(metric_name)
