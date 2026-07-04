import json
from dataclasses import replace

import pytest
from pathlib import Path

from src.application.evaluation.retrieval.retrieval_quality_gate import (
    RetrievalQualityGate,
)
from src.application.evaluation.retrieval.retrieval_quality_thresholds import (
    RetrievalQualityThresholds,
)
from src.shared.exceptions import SchemaValidationError


def _make_report(**overrides) -> dict:
    summary = {
        "hit_rate": 0.80,
        "mean_reciprocal_rank": 0.70,
        "recall_at_5": 0.75,
        "context_hit_rate": 0.72,
        "identifier_top_1_accuracy": 0.85,
    }
    summary.update(overrides)
    return {"summary": summary}


class TestRetrievalQualityGate:
    def test_passes_when_all_above_threshold(self):
        thresholds = RetrievalQualityThresholds(
            hit_rate=0.70,
            mrr=0.55,
            recall_at_5=0.65,
            context_hit_rate=0.60,
            identifier_top_1_accuracy=0.75,
        )
        gate = RetrievalQualityGate(thresholds=thresholds)
        result = gate.check(_make_report())
        assert result.passed
        assert result.violations == []

    def test_fails_when_hit_rate_below_threshold(self):
        thresholds = replace(RetrievalQualityThresholds.from_yaml(), hit_rate=0.80)
        gate = RetrievalQualityGate(thresholds=thresholds)
        result = gate.check(_make_report(hit_rate=0.75))
        assert not result.passed
        assert any(v.metric == "hit_rate" for v in result.violations)

    def test_fails_when_mrr_below_threshold(self):
        thresholds = replace(RetrievalQualityThresholds.from_yaml(), mrr=0.80)
        gate = RetrievalQualityGate(thresholds=thresholds)
        result = gate.check(_make_report(mean_reciprocal_rank=0.60))
        assert not result.passed

    def test_passes_when_threshold_disabled(self):
        thresholds = RetrievalQualityThresholds(
            hit_rate=None,
            mrr=None,
            recall_at_5=None,
            context_hit_rate=None,
            identifier_top_1_accuracy=None,
        )
        gate = RetrievalQualityGate(thresholds=thresholds)
        result = gate.check(_make_report(hit_rate=0.0))
        assert result.passed

    def test_violation_contains_actual_and_threshold(self):
        thresholds = replace(RetrievalQualityThresholds.from_yaml(), hit_rate=0.90)
        gate = RetrievalQualityGate(thresholds=thresholds)
        result = gate.check(_make_report(hit_rate=0.70))
        violation = next(v for v in result.violations if v.metric == "hit_rate")
        assert violation.actual == pytest.approx(0.70)
        assert violation.threshold == pytest.approx(0.90)

    def test_summary_says_pass(self):
        thresholds = replace(RetrievalQualityThresholds.from_yaml(), hit_rate=0.5)
        gate = RetrievalQualityGate(thresholds=thresholds)
        result = gate.check(_make_report(hit_rate=0.9))
        assert "PASS" in result.summary()

    def test_summary_says_fail(self):
        thresholds = replace(RetrievalQualityThresholds.from_yaml(), hit_rate=0.95)
        gate = RetrievalQualityGate(thresholds=thresholds)
        result = gate.check(_make_report(hit_rate=0.5))
        assert "FAIL" in result.summary()

    def test_handles_missing_metric_as_failure(self):
        thresholds = replace(RetrievalQualityThresholds.from_yaml(), hit_rate=0.70)
        gate = RetrievalQualityGate(thresholds=thresholds)
        result = gate.check({})
        assert not result.passed


class TestRetrievalQualityThresholds:
    def test_from_yaml_loads_file(self, tmp_path):
        yaml_path = tmp_path / "thresholds.yaml"
        yaml_path.write_text(
            "hit_rate: 0.80\nmrr: 0.65\nrecall_at_5: null\n",
            encoding="utf-8",
        )
        t = RetrievalQualityThresholds.from_yaml(yaml_path)
        assert t.hit_rate == pytest.approx(0.80)
        assert t.mrr == pytest.approx(0.65)
        assert t.recall_at_5 is None
        assert t.context_hit_rate is None
        assert t.identifier_top_1_accuracy is None

    def test_from_yaml_raises_when_file_missing(self, tmp_path):
        with pytest.raises(SchemaValidationError):
            RetrievalQualityThresholds.from_yaml(tmp_path / "nonexistent.yaml")
