from pathlib import Path

from src.application.evaluation.retrieval.benchmarking.datasets import (
    RetrievalBenchmarkDataset,
)
from src.application.evaluation.retrieval.benchmarking.loaders.markdown_section_parser import (
    extract_sections,
)
from src.application.evaluation.retrieval.benchmarking.loaders.retrieval_benchmark_case_block_parser import (
    extract_yaml_blocks,
    looks_like_case_block,
    parse_case_block,
)
from src.application.evaluation.retrieval.benchmarking.loaders.retrieval_benchmark_subset_table_parser import (
    parse_subset_definition,
)
from src.shared.exceptions import SchemaValidationError

DEFAULT_RETRIEVAL_TRUTH_SET_PATH = Path("TestDoc/retrieval_truth_set.md")


class RetrievalTruthSetLoader:
    def load(
        self,
        path: Path | str | None = None,
    ) -> RetrievalBenchmarkDataset:
        source_path = self._source_path(path)
        if not source_path.exists():
            raise SchemaValidationError(
                "Retrieval truth-set file not found.",
                details={"path": str(source_path)},
            )

        text = source_path.read_text(encoding="utf-8")
        sections = extract_sections(text)

        # Collect YAML blocks from the canonical section and any additional truth
        # sections that may have been appended as the corpus grew (e.g. section 10).
        # Blocks are only treated as cases if they carry a non-empty `id` field;
        # template / schema illustration blocks are thereby skipped automatically.
        all_yaml_blocks = [
            block
            for body in sections.values()
            for block in extract_yaml_blocks(body)
            if looks_like_case_block(block)
        ]
        cases = [
            parse_case_block(
                block_text,
                source_path=source_path,
                block_index=block_index,
            )
            for block_index, block_text in enumerate(
                all_yaml_blocks,
                start=1,
            )
        ]
        if not cases:
            raise SchemaValidationError(
                "Retrieval truth set did not contain any canonical cases.",
                details={"path": str(source_path)},
            )

        return RetrievalBenchmarkDataset(
            source_path=source_path,
            cases=cases,
            identifier_subset_definition=parse_subset_definition(
                sections.get("5"),
                subset_name="identifier-heavy",
                source_path=source_path,
            ),
            semantic_procedure_subset_definition=parse_subset_definition(
                sections.get("6"),
                subset_name="semantic-procedure",
                source_path=source_path,
            ),
        )

    @staticmethod
    def _source_path(path: Path | str | None) -> Path:
        if path is None:
            return DEFAULT_RETRIEVAL_TRUTH_SET_PATH
        return Path(path)
