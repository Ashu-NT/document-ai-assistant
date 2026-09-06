from src.application.reporting.document_parsing.graph_build_profiling import (
    build_structured_family_timing_summary,
    render_structured_family_timing_console_lines,
)


def _metric(
    name: str,
    elapsed_seconds: float,
    *,
    invocations: int = 0,
    specs: int = 0,
) -> dict[str, object]:
    return {
        "name": name,
        "elapsed_seconds": elapsed_seconds,
        "input_counts": {},
        "output_counts": {"specs": specs},
        "operations": {"invocations": invocations},
    }


def test_summary_ranks_dynamic_family_metrics_and_calculates_averages() -> None:
    summary = build_structured_family_timing_summary(
        [
            _metric("unrelated", 20.0),
            _metric("structured_family_spec_factory.select_specs", 12.0),
            _metric(
                "structured_family_spec_factory.select_specs.ManualBuilder",
                8.0,
                invocations=4,
                specs=6,
            ),
            _metric(
                "structured_family_spec_factory.select_specs.DrawingBuilder",
                3.0,
                invocations=2,
                specs=1,
            ),
        ]
    )

    assert summary["select_specs_elapsed_seconds"] == 12.0
    assert summary["family_elapsed_seconds"] == 11.0
    assert summary["unattributed_elapsed_seconds"] == 1.0
    assert summary["accounted_percent"] == 11.0 / 12.0 * 100.0
    families = summary["families"]
    assert families[0]["family_builder"] == "ManualBuilder"
    assert families[0]["average_milliseconds"] == 2000.0
    assert families[0]["specs"] == 6


def test_console_renderer_exposes_each_family_timing() -> None:
    summary = build_structured_family_timing_summary(
        [
            _metric("structured_family_spec_factory.select_specs", 2.0),
            _metric(
                "structured_family_spec_factory.select_specs.ReportBuilder",
                1.5,
                invocations=3,
                specs=4,
            ),
        ]
    )

    output = "\n".join(render_structured_family_timing_console_lines(summary))

    assert "select_specs=2.000s" in output
    assert "ReportBuilder" in output
    assert "calls=3" in output
    assert "avg= 500.000ms" in output
