def render_stage_metrics_table(
    *,
    title: str,
    metrics: list[dict[str, object]],
) -> list[str]:
    lines = [
        "",
        f"## {title}",
        "| Stage | Start | End | Elapsed | Inputs | Outputs | Operations |",
        "| --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for metric in metrics:
        lines.append(
            "| "
            f"{metric['name']} | "
            f"{float(metric['started_at_offset_seconds']):.3f}s | "
            f"{float(metric['ended_at_offset_seconds']):.3f}s | "
            f"{float(metric['elapsed_seconds']):.3f}s | "
            f"{_format_mapping(metric['input_counts'])} | "
            f"{_format_mapping(metric['output_counts'])} | "
            f"{_format_mapping(metric['operations'])} |"
        )
    return lines


def _format_mapping(value: object) -> str:
    if not isinstance(value, dict) or not value:
        return "-"
    return ", ".join(f"{key}={mapped}" for key, mapped in value.items())
