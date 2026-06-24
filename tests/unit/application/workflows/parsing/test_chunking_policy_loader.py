import pytest
from pathlib import Path

from src.application.workflows.parsing.builders.chunking.policies.chunking_policy_loader import (
    load_policy_from_yaml,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_policy_registry import (
    ChunkingPolicyRegistry,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)


def _write_yaml(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


class TestChunkingPolicyLoader:
    def test_returns_none_when_file_missing(self, tmp_path):
        policy = load_policy_from_yaml(ChunkingProfile.MANUAL, config_dir=tmp_path)
        assert policy is None

    def test_loads_manual_policy_from_yaml(self, tmp_path):
        _write_yaml(
            tmp_path / "manual.yaml",
            "max_chunk_tokens: 900\n"
            "chunk_overlap: 80\n"
            "same_topic_merge_tokens: 100\n"
            "intro_context_tokens: 150\n"
            "asset_context_window: 2\n"
            "asset_context_max_tokens: 80\n"
            "include_picture_chunks: true\n"
            "include_table_context: true\n",
        )
        policy = load_policy_from_yaml(ChunkingProfile.MANUAL, config_dir=tmp_path)
        assert policy is not None
        assert policy.max_chunk_tokens == 900
        assert policy.chunk_overlap == 80
        assert policy.profile_name == ChunkingProfile.MANUAL

    def test_returns_none_on_malformed_yaml(self, tmp_path):
        _write_yaml(tmp_path / "manual.yaml", "not: a: valid: policy")
        policy = load_policy_from_yaml(ChunkingProfile.MANUAL, config_dir=tmp_path)
        assert policy is None

    def test_loads_datasheet_policy(self, tmp_path):
        _write_yaml(
            tmp_path / "datasheet.yaml",
            "max_chunk_tokens: 500\n"
            "chunk_overlap: 50\n"
            "same_topic_merge_tokens: 60\n"
            "intro_context_tokens: 90\n"
            "asset_context_window: 1\n"
            "asset_context_max_tokens: 50\n"
            "include_picture_chunks: false\n"
            "include_table_context: true\n",
        )
        policy = load_policy_from_yaml(ChunkingProfile.DATASHEET, config_dir=tmp_path)
        assert policy is not None
        assert not policy.include_picture_chunks


class TestChunkingPolicyRegistry:
    def test_fallback_to_none_when_no_yaml(self, tmp_path):
        registry = ChunkingPolicyRegistry(config_dir=tmp_path)
        policy = registry.get(ChunkingProfile.MANUAL)
        assert policy is None

    def test_returns_policy_from_yaml(self, tmp_path):
        _write_yaml(
            tmp_path / "manual.yaml",
            "max_chunk_tokens: 800\n"
            "chunk_overlap: 90\n"
            "same_topic_merge_tokens: 110\n"
            "intro_context_tokens: 140\n"
            "asset_context_window: 2\n"
            "asset_context_max_tokens: 75\n",
        )
        registry = ChunkingPolicyRegistry(config_dir=tmp_path)
        policy = registry.get(ChunkingProfile.MANUAL)
        assert policy is not None
        assert policy.max_chunk_tokens == 800

    def test_caches_result(self, tmp_path):
        registry = ChunkingPolicyRegistry(config_dir=tmp_path)
        p1 = registry.get(ChunkingProfile.DRAWING)
        p2 = registry.get(ChunkingProfile.DRAWING)
        assert p1 is p2

    def test_resolver_uses_python_defaults_when_no_yaml(self, tmp_path):
        from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy_resolver import (
            DocumentChunkingPolicyResolver,
        )

        registry = ChunkingPolicyRegistry(config_dir=tmp_path)
        resolver = DocumentChunkingPolicyResolver(policy_registry=registry)
        policy = resolver._manual_policy()
        assert policy.max_chunk_tokens == 1000
