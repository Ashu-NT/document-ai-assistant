from dataclasses import replace

import pytest

from src.application.evaluation.parsing.parsing_performance_gate import (
    ParsingPerformanceGate,
)
from src.application.evaluation.parsing.parsing_performance_thresholds import (
    ParsingPerformanceThresholds,
)
from src.shared.exceptions import SchemaValidationError


class TestParsingPerformanceGate:
    def test_passes_when_all_stages_within_threshold(self):
        thresholds = ParsingPerformanceThresholds(
            docling_conversion_max_seconds=60.0,
            canonical_normalization_max_seconds=15.0,
            graph_build_max_seconds=10.0,
            total_max_seconds=90.0,
        )
        gate = ParsingPerformanceGate(thresholds=thresholds)

        result = gate.check(
            {
                "docling_conversion": 30.0,
                "canonical_normalization": 5.0,
                "graph_build": 2.0,
                "total": 40.0,
            }
        )

        assert result.passed
        assert result.violations == []

    def test_fails_when_docling_conversion_exceeds_threshold(self):
        thresholds = replace(
            ParsingPerformanceThresholds.from_yaml(),
            docling_conversion_max_seconds=10.0,
        )
        gate = ParsingPerformanceGate(thresholds=thresholds)

        result = gate.check({"docling_conversion": 15.0})

        assert not result.passed
        assert any(v.stage == "docling_conversion" for v in result.violations)

    def test_fails_when_stage_missing_from_measured_durations(self):
        thresholds = replace(
            ParsingPerformanceThresholds.from_yaml(),
            graph_build_max_seconds=10.0,
        )
        gate = ParsingPerformanceGate(thresholds=thresholds)

        result = gate.check({})

        assert not result.passed
        violation = next(v for v in result.violations if v.stage == "graph_build")
        assert violation.actual_seconds is None

    def test_passes_when_threshold_disabled(self):
        thresholds = ParsingPerformanceThresholds(
            docling_conversion_max_seconds=None,
            canonical_normalization_max_seconds=None,
            graph_build_max_seconds=None,
            total_max_seconds=None,
        )
        gate = ParsingPerformanceGate(thresholds=thresholds)

        result = gate.check({"docling_conversion": 99999.0})

        assert result.passed

    def test_violation_contains_actual_and_threshold(self):
        thresholds = replace(
            ParsingPerformanceThresholds.from_yaml(),
            total_max_seconds=50.0,
        )
        gate = ParsingPerformanceGate(thresholds=thresholds)

        result = gate.check({"total": 75.0})

        violation = next(v for v in result.violations if v.stage == "total")
        assert violation.actual_seconds == pytest.approx(75.0)
        assert violation.threshold_seconds == pytest.approx(50.0)

    def test_summary_says_pass(self):
        thresholds = ParsingPerformanceThresholds(
            docling_conversion_max_seconds=100.0,
            canonical_normalization_max_seconds=None,
            graph_build_max_seconds=None,
            total_max_seconds=None,
        )
        gate = ParsingPerformanceGate(thresholds=thresholds)

        result = gate.check({"docling_conversion": 5.0})

        assert "PASS" in result.summary()

    def test_summary_says_fail(self):
        thresholds = replace(
            ParsingPerformanceThresholds.from_yaml(),
            docling_conversion_max_seconds=1.0,
        )
        gate = ParsingPerformanceGate(thresholds=thresholds)

        result = gate.check({"docling_conversion": 5.0})

        assert "FAIL" in result.summary()


class TestParsingPerformanceThresholds:
    def test_from_yaml_loads_file(self, tmp_path):
        yaml_path = tmp_path / "thresholds.yaml"
        yaml_path.write_text(
            "docling_conversion_max_seconds: 45.0\n"
            "canonical_normalization_max_seconds: 10.0\n"
            "graph_build_max_seconds: null\n"
            "total_max_seconds: 90.0\n",
            encoding="utf-8",
        )

        t = ParsingPerformanceThresholds.from_yaml(yaml_path)

        assert t.docling_conversion_max_seconds == pytest.approx(45.0)
        assert t.canonical_normalization_max_seconds == pytest.approx(10.0)
        assert t.graph_build_max_seconds is None
        assert t.total_max_seconds == pytest.approx(90.0)

    def test_from_yaml_raises_when_file_missing(self, tmp_path):
        with pytest.raises(SchemaValidationError):
            ParsingPerformanceThresholds.from_yaml(tmp_path / "nonexistent.yaml")

    def test_default_yaml_is_calibrated_against_a_real_reference_document(self):
        """Locks in the 2026-07-04 calibration (see the YAML file's own
        comments for the reference document and methodology) so a future
        accidental revert to uncalibrated placeholder values doesn't go
        unnoticed. A real 64-page manual measured docling_conversion=349.4s
        and total=351.2s — thresholds must stay above that real baseline
        (with headroom) rather than drift back toward arbitrary guesses."""
        thresholds = ParsingPerformanceThresholds.from_yaml()

        assert thresholds.docling_conversion_max_seconds == pytest.approx(450.0)
        assert thresholds.canonical_normalization_max_seconds == pytest.approx(10.0)
        assert thresholds.graph_build_max_seconds == pytest.approx(10.0)
        assert thresholds.total_max_seconds == pytest.approx(480.0)

        gate = ParsingPerformanceGate(thresholds=thresholds)
        result = gate.check(
            {
                "docling_conversion": 349.37561359999745,
                "canonical_normalization": 0.8835923000006005,
                "graph_build": 0.9169074999990698,
                "graph_validation": 0.000816099996882258,
                "total": 351.1774011999987,
            }
        )
        assert result.passed, result.summary()
