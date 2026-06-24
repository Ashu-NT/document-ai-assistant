import pytest
from pathlib import Path

from src.application.workflows.parsing.markers.marker_config_loader import (
    load_marker_set,
)
from src.application.workflows.parsing.markers.marker_registry import MarkerRegistry
from src.application.workflows.parsing.markers.marker_set import MarkerSet


def _write_yaml(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


class TestMarkerSet:
    def test_get_returns_tuple(self):
        ms = MarkerSet(name="test", markers={"key1": ("a", "b", "c")})
        assert ms.get("key1") == ("a", "b", "c")

    def test_get_missing_key_returns_empty_tuple(self):
        ms = MarkerSet(name="test", markers={})
        assert ms.get("nonexistent") == ()

    def test_get_or_default_returns_default_when_missing(self):
        ms = MarkerSet(name="test", markers={})
        result = ms.get_or_default("key", ("x", "y"))
        assert result == ("x", "y")

    def test_get_or_default_returns_yaml_value_when_present(self):
        ms = MarkerSet(name="test", markers={"key": ("from_yaml",)})
        result = ms.get_or_default("key", ("default",))
        assert result == ("from_yaml",)


class TestMarkerConfigLoader:
    def test_returns_none_when_file_missing(self, tmp_path):
        result = load_marker_set("manual", config_dir=tmp_path)
        assert result is None

    def test_loads_markers_from_yaml(self, tmp_path):
        _write_yaml(
            tmp_path / "manual.yaml",
            "document:\n"
            "  - manual\n"
            "  - service manual\n"
            "maintenance_procedure:\n"
            "  - maintenance\n"
            "  - cleaning\n",
        )
        ms = load_marker_set("manual", config_dir=tmp_path)
        assert ms is not None
        assert ms.name == "manual"
        assert "manual" in ms.get("document")
        assert "service manual" in ms.get("document")
        assert "maintenance" in ms.get("maintenance_procedure")

    def test_returns_none_on_empty_yaml(self, tmp_path):
        _write_yaml(tmp_path / "manual.yaml", "")
        ms = load_marker_set("manual", config_dir=tmp_path)
        assert ms is None

    def test_returns_none_for_unknown_family(self, tmp_path):
        ms = load_marker_set("unknown_family_xyz", config_dir=tmp_path)
        assert ms is None


class TestMarkerRegistry:
    def test_get_returns_none_when_missing(self, tmp_path):
        registry = MarkerRegistry(config_dir=tmp_path)
        result = registry.get("manual")
        assert result is None

    def test_get_returns_marker_set_when_present(self, tmp_path):
        _write_yaml(
            tmp_path / "manual.yaml",
            "document:\n  - manual\n  - service manual\n",
        )
        registry = MarkerRegistry(config_dir=tmp_path)
        ms = registry.get("manual")
        assert ms is not None
        assert "manual" in ms.get("document")

    def test_get_markers_returns_none_on_missing(self, tmp_path):
        registry = MarkerRegistry(config_dir=tmp_path)
        result = registry.get_markers("manual", "document")
        assert result is None

    def test_get_markers_returns_tuple(self, tmp_path):
        _write_yaml(
            tmp_path / "manual.yaml",
            "document:\n  - manual\n",
        )
        registry = MarkerRegistry(config_dir=tmp_path)
        result = registry.get_markers("manual", "document")
        assert result == ("manual",)

    def test_caches_result(self, tmp_path):
        registry = MarkerRegistry(config_dir=tmp_path)
        r1 = registry.get("manual")
        r2 = registry.get("manual")
        assert r1 is r2
