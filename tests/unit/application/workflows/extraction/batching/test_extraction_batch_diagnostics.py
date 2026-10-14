from src.application.workflows.extraction.batching.extraction_batch_diagnostics import (
    hash_prompt,
    hash_prompt_canonical,
)


class TestHashPromptCanonical:
    def test_identical_prompts_hash_identically_both_ways(self) -> None:
        prompt = "Extract entities from chunk_05dca6fc2620466583210f3d6686a89a."

        assert hash_prompt(prompt) == hash_prompt(prompt)
        assert hash_prompt_canonical(prompt) == hash_prompt_canonical(prompt)

    def test_raw_hash_differs_when_only_the_embedded_id_differs(self) -> None:
        prompt_run1 = "Extract entities from chunk_05dca6fc2620466583210f3d6686a89a for doc_d6fc0fc0107344e299069cf6b5c999d3."
        prompt_run2 = "Extract entities from chunk_02255fa2ce124f5ba4698da3f10217a6 for doc_5c96511082bc4cbebeae27093b159eef."

        # The raw hash is sensitive to the embedded IDs - this is the exact
        # limitation this function exists to work around.
        assert hash_prompt(prompt_run1) != hash_prompt(prompt_run2)

    def test_canonical_hash_is_identical_when_only_the_embedded_id_differs(self) -> None:
        prompt_run1 = "Extract entities from chunk_05dca6fc2620466583210f3d6686a89a for doc_d6fc0fc0107344e299069cf6b5c999d3."
        prompt_run2 = "Extract entities from chunk_02255fa2ce124f5ba4698da3f10217a6 for doc_5c96511082bc4cbebeae27093b159eef."

        assert hash_prompt_canonical(prompt_run1) == hash_prompt_canonical(prompt_run2)

    def test_canonical_hash_still_differs_for_genuinely_different_content(self) -> None:
        prompt_run1 = "Extract entities from chunk_05dca6fc2620466583210f3d6686a89a: safety_warning only."
        prompt_run2 = "Extract entities from chunk_02255fa2ce124f5ba4698da3f10217a6: equipment_info only."

        assert hash_prompt_canonical(prompt_run1) != hash_prompt_canonical(prompt_run2)

    def test_canonicalization_does_not_mutate_the_input_string(self) -> None:
        prompt = "chunk_05dca6fc2620466583210f3d6686a89a stays as-is here"
        hash_prompt_canonical(prompt)

        assert prompt == "chunk_05dca6fc2620466583210f3d6686a89a stays as-is here"
