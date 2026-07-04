from src.application.prompts.extraction.candidate_router import (
    EXTRACTION_CANDIDATE_ROUTER_PROMPT_VERSION,
    ExtractionCandidateRouterPromptBuilder,
)


def test_build_includes_content_and_all_categories() -> None:
    builder = ExtractionCandidateRouterPromptBuilder()

    prompt = builder.build("Replace the filter every 1000 operating hours.")

    assert builder.prompt_version == EXTRACTION_CANDIDATE_ROUTER_PROMPT_VERSION
    assert "Replace the filter every 1000 operating hours." in prompt
    assert "- identifier:" in prompt
    assert "- manufacturer:" in prompt
    assert "- supplier:" in prompt
    assert "- equipment:" in prompt
    assert "- spare_part:" in prompt
    assert "- specification:" in prompt
    assert "- maintenance_task:" in prompt
    assert "- maintenance_interval:" in prompt
    assert "- procedure:" in prompt
    assert "- safety_warning:" in prompt
    assert "- troubleshooting:" in prompt
    assert '"candidate_types"' in prompt
